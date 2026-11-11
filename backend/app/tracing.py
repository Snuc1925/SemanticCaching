"""Trace từng request: mỗi bước pipeline là một span. Lưu Postgres, phát realtime qua Redis pub/sub -> SSE."""
from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from . import db
from .clients import rds

CHANNEL = "semcache:events"


class Trace:
    def __init__(self, user_id: str, username: str, question: str, session_id: str | None):
        self.id = str(uuid.uuid4())
        self.user_id, self.username, self.question, self.session_id = user_id, username, question, session_id
        self.t0 = time.perf_counter()
        self.created_at = datetime.now(timezone.utc)
        self.spans: list[dict] = []
        self.fields: dict = {"status": "ERROR"}

    @contextmanager
    def span(self, name: str, title: str):
        s = {"name": name, "title": title, "start_ms": round((time.perf_counter() - self.t0) * 1000, 1),
             "status": "ok", "data": {}}
        t = time.perf_counter()
        try:
            yield s["data"]
        except Exception as e:
            s["status"] = "error"
            s["data"]["error"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            s["duration_ms"] = round((time.perf_counter() - t) * 1000, 1)
            self.spans.append(s)

    def set(self, **kw) -> None:
        self.fields.update(kw)

    def elapsed_ms(self) -> float:
        return round((time.perf_counter() - self.t0) * 1000, 1)

    def save(self) -> None:
        f = self.fields
        db.execute(
            """INSERT INTO traces(id,created_at,user_id,username,session_id,question,status,policy,intent,partition,
               similarity,entry_id,latency_ms,llm_tokens_in,llm_tokens_out,embed_tokens,cost_usd,saved_tokens,
               saved_cost_usd,spans)
               VALUES (%(id)s,%(created_at)s,%(user_id)s,%(username)s,%(session_id)s,%(question)s,%(status)s,%(policy)s,
               %(intent)s,%(partition)s,%(similarity)s,%(entry_id)s,%(latency_ms)s,%(llm_tokens_in)s,%(llm_tokens_out)s,
               %(embed_tokens)s,%(cost_usd)s,%(saved_tokens)s,%(saved_cost_usd)s,%(spans)s)""",
            {"id": self.id, "created_at": self.created_at, "user_id": self.user_id, "username": self.username,
             "session_id": self.session_id, "question": self.question, "status": f.get("status"),
             "policy": f.get("policy"), "intent": f.get("intent"), "partition": f.get("partition"),
             "similarity": f.get("similarity"), "entry_id": f.get("entry_id"), "latency_ms": f.get("latency_ms"),
             "llm_tokens_in": f.get("llm_tokens_in", 0), "llm_tokens_out": f.get("llm_tokens_out", 0),
             "embed_tokens": f.get("embed_tokens", 0), "cost_usd": f.get("cost_usd", 0.0),
             "saved_tokens": f.get("saved_tokens", 0), "saved_cost_usd": f.get("saved_cost_usd", 0.0),
             "spans": db.Jsonb(self.spans)})
        publish("trace", summary(self.id))


def summary(trace_id: str) -> dict | None:
    row = db.fetch_one("""SELECT id,created_at,username,question,status,policy,intent,partition,similarity,latency_ms,
                          llm_tokens_in,llm_tokens_out,cost_usd,saved_tokens,saved_cost_usd,unauthorized,feedback
                          FROM traces WHERE id=%s""", (trace_id,))
    return jsonable(row) if row else None


def jsonable(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, uuid.UUID):
            out[k] = str(v)
        else:
            out[k] = v
    return out


def publish(kind: str, data) -> None:
    try:
        rds().publish(CHANNEL, json.dumps({"type": kind, "data": data}, ensure_ascii=False, default=str))
    except Exception:  # noqa: BLE001 - realtime là tiện ích, không làm hỏng request
        pass
