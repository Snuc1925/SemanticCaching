"""FastAPI app: API cho Chat (/api/...) và Console (/api/console/..., cần role ops_admin)."""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from contextlib import asynccontextmanager

import yaml
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from . import access, audit, cache, db, documents, metrics, pipeline, prompts
from .auth import console_user, console_user_from_query, current_user
from .clients import rds
from .config import data_dir, settings
from .iam.base import UserContext
from .sync import PermissionSync, publish_document_version
from .tracing import CHANNEL, Trace, jsonable

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("semcache")
SYNC: PermissionSync | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global SYNC
    db.init_schema()
    prompts.validate({pipeline.RAG_PROMPT: {"question", "context", "history", "no_answer"}})
    documents.ensure_collection()
    cache.ensure_collection()
    SYNC = PermissionSync()
    SYNC.start()
    log.info("backend sẵn sàng")
    yield
    SYNC.stop()


app = FastAPI(title="Permission-Aware Semantic Cache", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ------------------------------------------------------------------ chung
@app.get("/api/health")
def health():
    return {"ok": True, "sync_last_poll": SYNC.last_poll if SYNC else None,
            "sync_error": SYNC.last_error if SYNC else None}


@app.get("/api/me")
def me(user: UserContext = Depends(current_user)):
    sig = access.get(user)
    return {"user_id": user.user_id, "username": user.username, "name": user.display_name, "roles": list(user.roles),
            "is_console": settings()["keycloak"]["console_role"] in user.roles,
            "signature": sig.signature, "collections": sig.collections}


# ------------------------------------------------------------------ chat
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = None


def _own_session(session_id: str, user: UserContext) -> dict:
    s = db.fetch_one("SELECT * FROM sessions WHERE id=%s", (session_id,))
    if not s or s["user_id"] != user.user_id:     # lịch sử chat cũng phải phân quyền
        raise HTTPException(404, "Không tìm thấy session")
    return s


@app.post("/api/chat")
def chat(body: ChatIn, bg: BackgroundTasks, user: UserContext = Depends(current_user)):
    sid = body.session_id
    if sid:
        _own_session(sid, user)
    else:
        sid = str(uuid.uuid4())
        db.execute("INSERT INTO sessions(id,user_id,username,title) VALUES (%s,%s,%s,%s)",
                   (sid, user.user_id, user.username, body.message[:60]))
    history = [{"role": m["role"], "content": m["content"]} for m in db.fetch_all(
        "SELECT role, content FROM messages WHERE session_id=%s ORDER BY created_at DESC LIMIT 4", (sid,))][::-1]
    db.execute("INSERT INTO messages(id,session_id,role,content) VALUES (%s,%s,'user',%s)",
               (str(uuid.uuid4()), sid, body.message))
    tr = Trace(user.user_id, user.username, body.message, sid)
    try:
        res, _ = pipeline.answer(user, body.message, sid, history, tr)
    except Exception as e:  # noqa: BLE001
        log.exception("pipeline lỗi")
        tr.set(status="ERROR", latency_ms=tr.elapsed_ms())
        raise HTTPException(502, f"Lỗi xử lý: {e}") from e
    finally:
        try:
            tr.save()
        except Exception:  # noqa: BLE001
            log.exception("lưu trace lỗi")
    mid = str(uuid.uuid4())
    db.execute("""INSERT INTO messages(id,session_id,role,content,trace_id,cache_status,citations)
                  VALUES (%s,%s,'assistant',%s,%s,%s,%s)""",
               (mid, sid, res.answer, res.trace_id, res.status, db.Jsonb(res.citations)))
    db.execute("UPDATE sessions SET updated_at=now() WHERE id=%s", (sid,))
    bg.add_task(audit.run, res.trace_id, user, res.answer)
    return {"session_id": sid, "message_id": mid, "trace_id": res.trace_id, "status": res.status,
            "answer": res.answer, "citations": res.citations, "latency_ms": res.latency_ms,
            "similarity": res.similarity, "policy": res.policy}


@app.get("/api/sessions")
def sessions(user: UserContext = Depends(current_user)):
    rows = db.fetch_all("SELECT id,title,created_at,updated_at FROM sessions WHERE user_id=%s ORDER BY updated_at DESC",
                        (user.user_id,))
    return [jsonable(r) for r in rows]


@app.get("/api/sessions/{session_id}/messages")
def session_messages(session_id: str, user: UserContext = Depends(current_user)):
    _own_session(session_id, user)
    rows = db.fetch_all("""SELECT id,role,content,trace_id,cache_status,citations,feedback,created_at
                           FROM messages WHERE session_id=%s ORDER BY created_at""", (session_id,))
    return [jsonable(r) for r in rows]


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, user: UserContext = Depends(current_user)):
    _own_session(session_id, user)
    db.execute("DELETE FROM sessions WHERE id=%s", (session_id,))
    return {"ok": True}


class FeedbackIn(BaseModel):
    value: int = Field(ge=-1, le=1)


@app.post("/api/messages/{message_id}/feedback")
def feedback(message_id: str, body: FeedbackIn, user: UserContext = Depends(current_user)):
    m = db.fetch_one("""SELECT m.trace_id, s.user_id FROM messages m JOIN sessions s ON s.id=m.session_id
                        WHERE m.id=%s""", (message_id,))
    if not m or m["user_id"] != user.user_id:
        raise HTTPException(404, "Không tìm thấy tin nhắn")
    val = body.value or None
    db.execute("UPDATE messages SET feedback=%s WHERE id=%s", (val, message_id))
    if m["trace_id"]:
        db.execute("UPDATE traces SET feedback=%s WHERE id=%s", (val, m["trace_id"]))
    return {"ok": True}


# ------------------------------------------------------------------ console
@app.get("/api/console/metrics/overview")
def console_overview(minutes: int = 1440, _: UserContext = Depends(console_user)):
    return metrics.overview(minutes)


@app.get("/api/console/traces")
def console_traces(limit: int = 100, status: str | None = None, username: str | None = None,
                   _: UserContext = Depends(console_user)):
    return metrics.traces(limit, status, username)


@app.get("/api/console/traces/{trace_id}")
def console_trace(trace_id: str, _: UserContext = Depends(console_user)):
    t = metrics.trace(trace_id)
    if not t:
        raise HTTPException(404, "Không có trace")
    return t


@app.get("/api/console/cache/entries")
def console_cache_entries(_: UserContext = Depends(console_user)):
    return {"stats": cache.stats(), "partitions": access.partitions(), "entries": cache.list_entries()}


@app.delete("/api/console/cache")
def console_cache_flush(_: UserContext = Depends(console_user)):
    return {"deleted_keys": cache.flush()}


@app.get("/api/console/security/events")
def console_security(_: UserContext = Depends(console_user)):
    return {"events": metrics.security_events(), "revocation": metrics.revocation_stats(),
            "unauthorized_traces": [jsonable(r) for r in db.fetch_all(
                "SELECT id,created_at,username,question,status,audit FROM traces WHERE unauthorized ORDER BY created_at DESC LIMIT 50")]}


@app.get("/api/console/stream")
async def console_stream(_: UserContext = Depends(console_user_from_query)):
    async def gen():
        ps = rds().pubsub()
        ps.subscribe(CHANNEL)
        try:
            while True:
                msg = await asyncio.to_thread(ps.get_message, True, 1.0)
                if msg and msg.get("type") == "message":
                    d = json.loads(msg["data"])
                    yield {"event": d["type"], "data": json.dumps(d["data"], ensure_ascii=False, default=str)}
                else:
                    yield {"event": "ping", "data": "{}"}
        finally:
            ps.close()
    return EventSourceResponse(gen())


# ---- admin (phục vụ demo + Playwright)
def _acl() -> dict:
    return yaml.safe_load((data_dir() / "acl.yaml").read_text(encoding="utf-8"))


@app.get("/api/console/admin/users")
def admin_users(_: UserContext = Depends(console_user)):
    acl = _acl()
    adm = access.adapter().admin
    out = []
    for u in acl["users"]:
        info = adm.find_user(u["username"])
        if not info:
            continue
        uc = UserContext(info["id"], u["username"])
        roles = sorted(r for r in adm.user_realm_roles(info["id"]) if r in {x["name"] for x in acl["roles"]})
        raw = rds().get(f"sig:user:{info['id']}")
        cached = json.loads(raw) if raw else None
        out.append({"username": u["username"], "name": u.get("name"), "user_id": info["id"], "roles": roles,
                    "attributes": {k: v[0] for k, v in (info.get("attributes") or {}).items()},
                    "collections_now": sorted(access.adapter().list_accessible_collections(uc)),
                    "cached_signature": cached})
    return {"users": out, "roles": [r["name"] for r in acl["roles"]], "collections": list(acl["collections"])}


class RoleIn(BaseModel):
    role: str
    grant: bool


@app.post("/api/console/admin/users/{username}/roles")
def admin_set_role(username: str, body: RoleIn, actor: UserContext = Depends(console_user)):
    acl = _acl()
    if body.role not in {r["name"] for r in acl["roles"]}:
        raise HTTPException(400, "Role không hợp lệ")
    if username == actor.username and body.role == settings()["keycloak"]["console_role"] and not body.grant:
        raise HTTPException(400, "Không tự thu hồi quyền Console của chính mình")
    adm = access.adapter().admin
    info = adm.find_user(username)
    if not info:
        raise HTTPException(404, "Không có user")
    adm.set_realm_role(info["id"], body.role, body.grant)
    # Không tự xoá signature ở đây: để luồng admin-events -> PermissionSync xử lý, giống như khi
    # quản trị viên đổi quyền trực tiếp trong Keycloak (đo được revocation window thật).
    return {"ok": True, "username": username, "role": body.role, "grant": body.grant}


@app.get("/api/console/admin/documents")
def admin_documents(_: UserContext = Depends(console_user)):
    return documents.list_documents()


class PublishIn(BaseModel):
    version: int


@app.post("/api/console/admin/documents/{doc_id}/publish")
def admin_publish(doc_id: str, body: PublishIn, actor: UserContext = Depends(console_user)):
    info = documents.available_versions().get(doc_id)
    if not info or body.version not in info["versions"]:
        raise HTTPException(404, "Không có version này")
    return publish_document_version(doc_id, body.version, actor.username)


class ResetIn(BaseModel):
    clear_history: bool = False


@app.post("/api/console/admin/reset")
def admin_reset(body: ResetIn, actor: UserContext = Depends(console_user)):
    """Đưa demo về trạng thái ban đầu: quyền theo acl.yaml, tài liệu version đầu, cache rỗng."""
    acl = _acl()
    adm = access.adapter().admin
    managed = {r["name"] for r in acl["roles"]}
    for u in acl["users"]:
        info = adm.find_user(u["username"])
        if not info:
            continue
        have = set(adm.user_realm_roles(info["id"])) & managed
        want = set(u["roles"])
        for r in want - have:
            adm.set_realm_role(info["id"], r, True)
        for r in have - want:
            adm.set_realm_role(info["id"], r, False)
    for d in documents.list_documents():
        first = min(d["versions"])
        if d["current_version"] != first:
            documents.ingest(d["doc_id"], first)
    cache.flush()
    access.invalidate_all()
    rds().delete("sig:known")
    if body.clear_history:
        db.execute("DELETE FROM traces; DELETE FROM security_events; DELETE FROM sessions;")
    return {"ok": True}
