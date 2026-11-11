"""Kho tài liệu: đọc file Markdown (có front matter), chunk, embed, lưu Qdrant; quản lý version."""
from __future__ import annotations

import re
from pathlib import Path

import yaml
from qdrant_client import models as qm

from . import db, embeddings
from .chunking import chunk_document
from .clients import qdrant, rds
from .config import data_dir, settings

CHUNKS = "chunks"
_FM = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)


def docs_dir() -> Path:
    return data_dir() / "docs"


def parse_file(path: Path) -> tuple[dict, str]:
    m = _FM.match(path.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{path} thiếu front matter")
    return yaml.safe_load(m.group(1)), m.group(2)


def available_versions() -> dict[str, dict]:
    """doc_id -> {title, collection, versions: [..]} từ các file <doc_id>.v<N>.md."""
    out: dict[str, dict] = {}
    for p in sorted(docs_dir().glob("*.v*.md")):
        meta, _ = parse_file(p)
        d = out.setdefault(meta["doc_id"], {"title": meta["title"], "collection": meta["collection"], "versions": []})
        d["versions"].append(int(meta["version"]))
    return out


def file_for(doc_id: str, version: int) -> Path:
    return docs_dir() / f"{doc_id}.v{version}.md"


def ensure_collection() -> None:
    q = qdrant()
    if not q.collection_exists(CHUNKS):
        q.create_collection(CHUNKS, vectors_config=qm.VectorParams(size=embeddings.dim(), distance=qm.Distance.COSINE))
        q.create_payload_index(CHUNKS, "collection", qm.PayloadSchemaType.KEYWORD)
        q.create_payload_index(CHUNKS, "doc_id", qm.PayloadSchemaType.KEYWORD)


def current_version(doc_id: str) -> int | None:
    v = rds().hget("doc:version", doc_id)
    if v is None:
        row = db.fetch_one("SELECT version FROM documents WHERE doc_id=%s", (doc_id,))
        if not row:
            return None
        rds().hset("doc:version", doc_id, row["version"])
        return row["version"]
    return int(v)


def current_versions(doc_ids: list[str]) -> dict[str, int | None]:
    if not doc_ids:
        return {}
    vals = rds().hmget("doc:version", doc_ids)
    return {d: (int(v) if v is not None else current_version(d)) for d, v in zip(doc_ids, vals)}


def ingest(doc_id: str, version: int) -> int:
    """Nạp 1 version của tài liệu: xoá chunk cũ của doc_id, thêm chunk mới, cập nhật version. Trả số chunk."""
    meta, body = parse_file(file_for(doc_id, version))
    c = settings()["chunking"]
    chunks = chunk_document(doc_id, version, meta["collection"], meta["title"], body,
                            c["max_tokens"], c["min_tokens"], c["overlap_tokens"])
    vecs, _, _ = embeddings.embed([ch.embed_text for ch in chunks])
    ensure_collection()
    q = qdrant()
    q.delete(CHUNKS, points_selector=qm.FilterSelector(filter=qm.Filter(
        must=[qm.FieldCondition(key="doc_id", match=qm.MatchValue(value=doc_id))])))
    import uuid
    q.upsert(CHUNKS, points=[
        qm.PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, ch.chunk_id)), vector=v, payload={
            "chunk_id": ch.chunk_id, "doc_id": ch.doc_id, "version": ch.version, "collection": ch.collection,
            "title": ch.title, "section_path": ch.section_path, "text": ch.text})
        for ch, v in zip(chunks, vecs)])
    db.execute("""INSERT INTO documents(doc_id,title,collection,version,updated_at) VALUES (%s,%s,%s,%s,now())
                  ON CONFLICT (doc_id) DO UPDATE SET title=EXCLUDED.title, collection=EXCLUDED.collection,
                  version=EXCLUDED.version, updated_at=now()""",
               (doc_id, meta["title"], meta["collection"], version))
    rds().hset("doc:version", doc_id, version)
    return len(chunks)


def ingest_all_initial() -> dict[str, int]:
    """Nạp version nhỏ nhất của mọi tài liệu (trạng thái ban đầu của demo)."""
    out = {}
    for doc_id, info in available_versions().items():
        out[doc_id] = ingest(doc_id, min(info["versions"]))
    return out


def list_documents() -> list[dict]:
    rows = {r["doc_id"]: r for r in db.fetch_all("SELECT * FROM documents ORDER BY collection, doc_id")}
    out = []
    for doc_id, info in available_versions().items():
        r = rows.get(doc_id)
        out.append({"doc_id": doc_id, "title": info["title"], "collection": info["collection"],
                    "versions": info["versions"], "current_version": r["version"] if r else None,
                    "updated_at": r["updated_at"].isoformat() if r else None})
    return out
