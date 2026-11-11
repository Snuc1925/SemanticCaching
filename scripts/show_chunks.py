"""Xem dữ liệu đang lưu trong Qdrant (chỉ đọc, không gọi API ngoài).

    .venv/bin/python scripts/show_chunks.py                    # mọi chunk, nhóm theo tài liệu
    .venv/bin/python scripts/show_chunks.py --doc return_policy
    .venv/bin/python scripts/show_chunks.py --collection cskh
    .venv/bin/python scripts/show_chunks.py --summary          # chỉ thống kê
    .venv/bin/python scripts/show_chunks.py --cache            # các câu hỏi đang nằm trong semantic cache
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from qdrant_client import models as qm  # noqa: E402

from app.chunking import ntokens  # noqa: E402
from app.clients import qdrant, rds  # noqa: E402


def scroll(collection: str, flt: qm.Filter | None = None) -> list:
    out, offset = [], None
    while True:
        pts, offset = qdrant().scroll(collection, scroll_filter=flt, limit=256, offset=offset,
                                      with_payload=True, with_vectors=False)
        out += pts
        if offset is None:
            return out


def show_chunks(args) -> None:
    must = []
    if args.doc:
        must.append(qm.FieldCondition(key="doc_id", match=qm.MatchValue(value=args.doc)))
    if args.collection:
        must.append(qm.FieldCondition(key="collection", match=qm.MatchValue(value=args.collection)))
    pts = scroll("chunks", qm.Filter(must=must) if must else None)
    by_doc: dict[str, list] = defaultdict(list)
    for p in pts:
        by_doc[p.payload["doc_id"]].append(p.payload)
    print(f"{len(pts)} chunk / {len(by_doc)} tài liệu\n")
    for doc_id in sorted(by_doc):
        chunks = sorted(by_doc[doc_id], key=lambda c: c["section_path"])
        c0 = chunks[0]
        print(f"=== {doc_id}  (v{c0['version']}, collection={c0['collection']}, {len(chunks)} chunk)")
        if args.summary:
            continue
        for c in chunks:
            print(f"--- chunk_id={c['chunk_id']}  tokens={ntokens(c['text'])}")
            print(f"    [{c['section_path']}]")
            for line in c["text"].splitlines():
                print(f"    {line}")
        print()


def show_cache() -> None:
    import json
    r = rds()
    ids = r.zrevrange("cache:lru", 0, -1)
    print(f"{len(ids)} entry trong cache\n")
    for eid in ids:
        raw = r.get(f"cache:entry:{eid}")
        if not raw:
            continue
        e = json.loads(raw)
        docs = sorted({f"{p['doc_id']} v{p['version']}" for p in e["provenance"]})
        print(f"- [{e['partition']}] {e['question']}  (hits={e['hits']}, intent={e['intent']})")
        print(f"    nguồn: {', '.join(docs)}")
        print(f"    trả lời: {e['answer'][:160]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc")
    ap.add_argument("--collection")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--cache", action="store_true")
    a = ap.parse_args()
    show_cache() if a.cache else show_chunks(a)
