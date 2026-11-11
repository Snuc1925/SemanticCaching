"""Permission-aware semantic cache (plan mục 4.2, 4.4, 4.5, 4.6, 4.9).

Lưu trữ:
  - Qdrant collection "semantic_cache": vector câu hỏi + payload {entry_id, partition}
  - Redis  cache:entry:<id>   JSON entry (answer, provenance, ...)
           cache:doc:<doc_id> set entry_id   (reverse index: tài liệu -> entry dùng nó)
           cache:lru          zset entry_id -> lần truy cập cuối (eviction LRU)

Điều kiện một entry được HIT (mục 4.5), kiểm theo thứ tự, ghi lại lý do trượt cho Console:
  1. cùng partition (= access signature)         -> lọc ngay trong Qdrant
  2. similarity >= ngưỡng của intent
  3. entity khớp (vd gói Bạc != gói Vàng)
  4. provenance còn hiệu lực: version tài liệu + version prompt
  5. chưa hết TTL
  6. (tuỳ chọn) IAM re-verify các collection trong provenance
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field

from qdrant_client import models as qm

from . import documents, embeddings
from .clients import qdrant, rds
from .config import settings

CACHE = "semantic_cache"


@dataclass
class Provenance:
    chunk_id: str
    doc_id: str
    version: int
    collection: str
    title: str = ""
    section_path: str = ""


@dataclass
class CacheEntry:
    entry_id: str
    partition: str
    question: str
    answer: str
    citations: list[dict]
    provenance: list[Provenance]
    intent: str
    entities: dict[str, str]
    policy: str
    prompt_version: str
    model: str
    created_at: float
    ttl: int
    gen_tokens_in: int
    gen_tokens_out: int
    gen_cost_usd: float
    gen_latency_ms: float
    hits: int = 0
    last_hit: float | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_json(s: str) -> "CacheEntry":
        d = json.loads(s)
        d["provenance"] = [Provenance(**p) for p in d["provenance"]]
        return CacheEntry(**d)


@dataclass
class Candidate:
    entry_id: str
    question: str
    similarity: float
    threshold: float
    passed: bool
    reason: str


@dataclass
class LookupResult:
    hit: CacheEntry | None
    similarity: float | None
    candidates: list[Candidate] = field(default_factory=list)


def ensure_collection() -> None:
    q = qdrant()
    if not q.collection_exists(CACHE):
        q.create_collection(CACHE, vectors_config=qm.VectorParams(size=embeddings.dim(), distance=qm.Distance.COSINE))
        q.create_payload_index(CACHE, "partition", qm.PayloadSchemaType.KEYWORD)


def threshold_for(intent: str) -> float:
    c = settings()["cache"]
    return float(c.get("threshold_by_intent", {}).get(intent, c["threshold_default"]))


def get_entry(entry_id: str) -> CacheEntry | None:
    raw = rds().get(f"cache:entry:{entry_id}")
    return CacheEntry.from_json(raw) if raw else None


def lookup(vec: list[float], partition: str, intent: str, entities: dict[str, str], prompt_version: str,
           reverify=None) -> LookupResult:
    """reverify(collections:set[str]) -> dict[str,bool]  (điều kiện 6, có thể None)."""
    c = settings()["cache"]
    res = qdrant().query_points(
        CACHE, query=vec, limit=c["candidates"], with_payload=True,
        query_filter=qm.Filter(must=[qm.FieldCondition(key="partition", match=qm.MatchValue(value=partition))]),
    ).points
    out = LookupResult(None, res[0].score if res else None)
    tau = threshold_for(intent)
    now = time.time()
    for p in res:
        eid = p.payload["entry_id"]
        e = get_entry(eid)
        if e is None:                           # entry đã hết TTL trong Redis -> dọn vector mồ côi
            _delete_vector(eid)
            out.candidates.append(Candidate(eid, "?", p.score, tau, False, "entry đã hết hạn (TTL)"))
            continue
        cand = Candidate(eid, e.question, p.score, tau, False, "")
        if p.score < tau:
            cand.reason = f"similarity {p.score:.3f} < ngưỡng {tau:.2f}"
        elif e.entities != entities:
            cand.reason = f"entity khác: câu hỏi {entities or '{}'} vs entry {e.entities or '{}'}"
        elif e.prompt_version != prompt_version:
            cand.reason = f"prompt đã đổi ({e.prompt_version} -> {prompt_version})"
        elif (stale := _stale_docs(e)):
            cand.reason = "tài liệu đã đổi version: " + ", ".join(stale)
        elif now - e.created_at > e.ttl:
            cand.reason = "hết TTL"
        else:
            denied = []
            if reverify is not None:
                cols = {pv.collection for pv in e.provenance}
                decisions = reverify(cols)
                denied = sorted(col for col in cols if not decisions.get(col, False))
            if denied:
                cand.reason = "IAM re-verify từ chối collection: " + ", ".join(denied)
            else:
                cand.passed, cand.reason = True, "thoả mọi điều kiện"
        out.candidates.append(cand)
        if cand.passed and out.hit is None:
            out.hit, out.similarity = e, p.score
            _touch(e)
            break
    return out


def _stale_docs(e: CacheEntry) -> list[str]:
    cur = documents.current_versions(sorted({p.doc_id for p in e.provenance}))
    stale = []
    for p in e.provenance:
        v = cur.get(p.doc_id)
        if v is None or v != p.version:
            stale.append(f"{p.doc_id} v{p.version}->v{v}")
    return sorted(set(stale))


def _touch(e: CacheEntry) -> None:
    e.hits += 1
    e.last_hit = time.time()
    ttl_left = max(1, int(e.created_at + e.ttl - time.time()))
    rds().set(f"cache:entry:{e.entry_id}", e.to_json(), ex=ttl_left)
    rds().zadd("cache:lru", {e.entry_id: e.last_hit})


def store(e: CacheEntry, vec: list[float]) -> None:
    ensure_collection()
    qdrant().upsert(CACHE, points=[qm.PointStruct(id=e.entry_id, vector=vec,
                                                  payload={"entry_id": e.entry_id, "partition": e.partition})])
    r = rds()
    pipe = r.pipeline()
    pipe.set(f"cache:entry:{e.entry_id}", e.to_json(), ex=e.ttl)
    for doc_id in {p.doc_id for p in e.provenance}:
        pipe.sadd(f"cache:doc:{doc_id}", e.entry_id)
    pipe.zadd("cache:lru", {e.entry_id: e.created_at})
    pipe.execute()
    evict_if_needed()


def new_entry_id() -> str:
    return str(uuid.uuid4())


def _delete_vector(entry_id: str) -> None:
    qdrant().delete(CACHE, points_selector=qm.PointIdsList(points=[entry_id]))


def delete(entry_id: str) -> None:
    e = get_entry(entry_id)
    r = rds()
    pipe = r.pipeline()
    if e:
        for doc_id in {p.doc_id for p in e.provenance}:
            pipe.srem(f"cache:doc:{doc_id}", entry_id)
    pipe.delete(f"cache:entry:{entry_id}")
    pipe.zrem("cache:lru", entry_id)
    pipe.execute()
    _delete_vector(entry_id)


def invalidate_doc(doc_id: str) -> list[str]:
    """Xoá mọi entry có provenance chứa doc_id (reverse index, plan mục 4.6)."""
    ids = list(rds().smembers(f"cache:doc:{doc_id}"))
    for eid in ids:
        delete(eid)
    rds().delete(f"cache:doc:{doc_id}")
    if ids:
        rds().hincrby("cache:stats", "invalidated_doc_update", len(ids))
    return ids


def evict_if_needed() -> list[str]:
    """Eviction LRU khi vượt max_entries. (Các policy khác: thí nghiệm E4, Giai đoạn C.)"""
    r = rds()
    limit = settings()["cache"]["max_entries"]
    n = r.zcard("cache:lru")
    if n <= limit:
        return []
    victims = r.zrange("cache:lru", 0, n - limit - 1)
    for eid in victims:
        delete(eid)
    r.hincrby("cache:stats", "evicted_lru", len(victims))
    return victims


def list_entries(limit: int = 200) -> list[dict]:
    r = rds()
    ids = r.zrevrange("cache:lru", 0, limit - 1)
    out = []
    for eid in ids:
        e = get_entry(eid)
        if not e:
            r.zrem("cache:lru", eid)
            continue
        d = asdict(e)
        d["ttl_left"] = int(e.created_at + e.ttl - time.time())
        out.append(d)
    return out


def flush() -> int:
    r = rds()
    keys = list(r.scan_iter("cache:*"))
    if keys:
        r.delete(*keys)
    q = qdrant()
    if q.collection_exists(CACHE):
        q.delete_collection(CACHE)
    ensure_collection()
    return len(keys)


def stats() -> dict:
    r = rds()
    s = {k: int(v) for k, v in r.hgetall("cache:stats").items()}
    s["entries"] = r.zcard("cache:lru")
    return s
