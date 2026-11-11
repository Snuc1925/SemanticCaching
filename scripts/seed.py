"""Nạp dữ liệu pilot: tạo schema, ingest version đầu của mọi tài liệu, xoá cache, xoá signature.
    .venv/bin/python scripts/seed.py [--clear-history]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import access, cache, db, documents  # noqa: E402
from app.clients import rds  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clear-history", action="store_true", help="xoá trace, session, security events")
    args = ap.parse_args()
    db.init_schema()
    if args.clear_history:
        db.execute("DELETE FROM traces; DELETE FROM security_events; DELETE FROM sessions; DELETE FROM documents;")
    rds().delete("doc:version", "sig:known")
    res = documents.ingest_all_initial()
    for doc_id, n in res.items():
        print(f"  ingested {doc_id:24s} {n} chunk")
    cache.flush()
    access.invalidate_all()
    print(f"OK: {len(res)} tài liệu, {sum(res.values())} chunk; cache đã xoá")


if __name__ == "__main__":
    main()
