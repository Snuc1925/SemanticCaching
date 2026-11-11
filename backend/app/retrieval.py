"""Retrieval: PRE-FILTER theo collection trong access signature (plan 4.3), sau đó IAM post-verify.

Khác PermRAG gốc: PermRAG lấy top-k trên toàn corpus rồi mới lọc -> user ít quyền bị "đói" context.
Ở đây Qdrant chỉ tìm trong các collection user được đọc theo snapshot (signature); IAM vẫn là trọng tài cuối.
"""
from __future__ import annotations

from dataclasses import dataclass

from qdrant_client import models as qm

from .clients import qdrant
from .config import settings
from .documents import CHUNKS


@dataclass
class Retrieved:
    label: str
    chunk_id: str
    doc_id: str
    version: int
    collection: str
    title: str
    section_path: str
    text: str
    score: float


def search(vec: list[float], collections: list[str], top_k: int | None = None) -> list[Retrieved]:
    if not collections:
        return []
    cfg = settings()["retrieval"]
    pts = qdrant().query_points(
        CHUNKS, query=vec, limit=top_k or cfg["top_k"], with_payload=True,
        query_filter=qm.Filter(must=[qm.FieldCondition(key="collection", match=qm.MatchAny(any=collections))]),
    ).points
    out = []
    for p in pts:
        if p.score < cfg["min_score"]:
            continue
        pl = p.payload
        out.append(Retrieved("", pl["chunk_id"], pl["doc_id"], pl["version"], pl["collection"], pl["title"],
                             pl["section_path"], pl["text"], p.score))
    return out


def format_context(chunks: list[Retrieved]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        c.label = f"c{i}"
        parts.append(f"[{c.label}] (Nguồn: {c.section_path})\n{c.text}")
    return "\n\n".join(parts)
