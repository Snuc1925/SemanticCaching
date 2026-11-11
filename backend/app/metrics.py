"""Tổng hợp metric cho Console (plan mục 7). Phần theo dõi vận hành; đánh giá chi tiết E1–E7 ở Giai đoạn C."""
from __future__ import annotations

from . import access, cache, db
from .tracing import jsonable


def overview(minutes: int = 1440) -> dict:
    p = {"m": minutes}
    tot = db.fetch_one("""
        SELECT count(*) AS requests,
               count(*) FILTER (WHERE status='HIT')  AS hits,
               count(*) FILTER (WHERE status='MISS') AS misses,
               count(*) FILTER (WHERE status='BYPASS') AS bypass,
               count(*) FILTER (WHERE status='NO_CACHE') AS no_cache,
               count(*) FILTER (WHERE status='ERROR') AS errors,
               coalesce(sum(llm_tokens_in+llm_tokens_out),0) AS llm_tokens,
               coalesce(sum(saved_tokens),0) AS saved_tokens,
               coalesce(sum(cost_usd),0) AS cost_usd,
               coalesce(sum(saved_cost_usd),0) AS saved_cost_usd,
               count(*) FILTER (WHERE unauthorized) AS unauthorized,
               count(*) FILTER (WHERE audit IS NOT NULL) AS audited,
               count(*) FILTER (WHERE status='HIT' AND feedback=-1) AS hit_negative_feedback,
               count(*) FILTER (WHERE status='HIT' AND feedback IS NOT NULL) AS hit_feedback
        FROM traces WHERE created_at > now() - make_interval(mins => %(m)s)""", p)
    lat = db.fetch_all("""
        SELECT status, count(*) AS n,
               percentile_cont(0.5)  WITHIN GROUP (ORDER BY latency_ms) AS p50,
               percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95
        FROM traces WHERE created_at > now() - make_interval(mins => %(m)s) AND latency_ms IS NOT NULL
        GROUP BY status""", p)
    series = db.fetch_all("""
        SELECT date_trunc('minute', created_at) AS t,
               count(*) AS requests,
               count(*) FILTER (WHERE status='HIT') AS hits,
               count(*) FILTER (WHERE status='MISS') AS misses,
               avg(latency_ms) AS avg_latency
        FROM traces WHERE created_at > now() - make_interval(mins => %(m)s)
        GROUP BY 1 ORDER BY 1""", p)
    by_intent = db.fetch_all("""
        SELECT coalesce(intent,'-') AS intent, count(*) AS requests,
               count(*) FILTER (WHERE status='HIT') AS hits,
               count(*) FILTER (WHERE status='MISS') AS misses,
               count(*) FILTER (WHERE status='HIT' AND feedback=-1) AS hit_negative_feedback,
               avg(similarity) FILTER (WHERE status='HIT') AS avg_hit_similarity
        FROM traces WHERE created_at > now() - make_interval(mins => %(m)s)
        GROUP BY 1 ORDER BY 2 DESC""", p)
    cacheable = (tot["hits"] or 0) + (tot["misses"] or 0)
    return {
        "window_minutes": minutes,
        "totals": tot,
        "hit_rate": (tot["hits"] / cacheable) if cacheable else None,
        "false_hit_rate_feedback": (tot["hit_negative_feedback"] / tot["hit_feedback"]) if tot["hit_feedback"] else None,
        "latency": {r["status"]: {"n": r["n"], "p50": r["p50"], "p95": r["p95"]} for r in lat},
        "series": [jsonable(r) for r in series],
        "by_intent": by_intent,
        "cache": cache.stats(),
        "partitions": access.partitions(),
        "revocation": revocation_stats(),
    }


def revocation_stats() -> dict:
    r = db.fetch_one("""
        SELECT count(*) AS n,
               avg(extract(epoch FROM effective_at - occurred_at)) AS avg_s,
               max(extract(epoch FROM effective_at - occurred_at)) AS max_s
        FROM security_events WHERE kind='permission_change' AND effective_at IS NOT NULL""")
    return r or {}


def traces(limit: int = 100, status: str | None = None, username: str | None = None) -> list[dict]:
    q = """SELECT id,created_at,username,question,status,policy,intent,partition,similarity,latency_ms,
                  llm_tokens_in,llm_tokens_out,cost_usd,saved_tokens,saved_cost_usd,unauthorized,feedback
           FROM traces WHERE (%(s)s::text IS NULL OR status=%(s)s) AND (%(u)s::text IS NULL OR username=%(u)s)
           ORDER BY created_at DESC LIMIT %(l)s"""
    return [jsonable(r) for r in db.fetch_all(q, {"s": status, "u": username, "l": limit})]


def trace(trace_id: str) -> dict | None:
    r = db.fetch_one("SELECT * FROM traces WHERE id=%s", (trace_id,))
    return jsonable(r) if r else None


def security_events(limit: int = 100) -> list[dict]:
    rows = db.fetch_all("SELECT * FROM security_events ORDER BY occurred_at DESC LIMIT %s", (limit,))
    out = []
    for r in rows:
        d = jsonable(r)
        if r["effective_at"]:
            d["window_seconds"] = (r["effective_at"] - r["occurred_at"]).total_seconds()
        out.append(d)
    return out
