"""Audit rò rỉ bằng canary (plan mục 5.1, metric "Unauthorized serve").

Sau mỗi câu trả lời (chạy nền, không tính vào latency): tìm canary trong câu trả lời; nếu canary thuộc
collection mà user KHÔNG có quyền theo đánh giá IAM *tại thời điểm audit* -> unauthorized serve.
"""
from __future__ import annotations

import re
from functools import lru_cache

import yaml

from . import db
from .access import adapter
from .config import data_dir
from .iam.base import UserContext
from .tracing import publish


@lru_cache
def canaries() -> list[dict]:
    p = data_dir() / "canaries.yaml"
    if not p.exists():
        return []
    items = yaml.safe_load(p.read_text(encoding="utf-8"))["canaries"]
    for c in items:
        c["_re"] = re.compile(c["pattern"], re.I)
    return items


def find(text: str) -> list[dict]:
    return [{"id": c["id"], "collection": c["collection"]} for c in canaries() if c["_re"].search(text or "")]


def run(trace_id: str, user: UserContext, answer: str) -> dict:
    found = find(answer)
    result = {"canaries": found, "denied_collections": [], "checked_with_iam": False}
    if found:
        cols = {c["collection"] for c in found}
        decisions = adapter().check_collections(user, cols)
        result["checked_with_iam"] = True
        result["denied_collections"] = sorted(c for c in cols if not decisions.get(c, False))
    unauthorized = bool(result["denied_collections"])
    db.execute("UPDATE traces SET audit=%s, unauthorized=%s WHERE id=%s", (db.Jsonb(result), unauthorized, trace_id))
    publish("audit", {"id": trace_id, "unauthorized": unauthorized, "audit": result})
    return result
