"""Đồng bộ thay đổi quyền/tài liệu (plan mục 4.6, 4.7).

- Thread nền poll Keycloak admin-events mỗi `event_poll_seconds` -> xoá signature của user bị ảnh hưởng
  (lần hỏi tiếp theo signature được tính lại -> user tự động sang partition đúng).
- Ghi security_events: occurred_at (Keycloak) / detected_at / effective_at -> Console tính revocation window.
- Cập nhật tài liệu: nạp version mới -> invalidate entry qua reverse index.
"""
from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone

from . import access, cache, db, documents
from .config import settings
from .iam.keycloak import KeycloakAdmin, KeycloakEventSource
from .tracing import publish

log = logging.getLogger("semcache.sync")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def record_event(kind: str, source: str, occurred_at: datetime, detected_at: datetime,
                 effective_at: datetime | None, summary: str, details: dict) -> dict:
    row = db.fetch_one(
        """INSERT INTO security_events(kind,source,occurred_at,detected_at,effective_at,summary,details)
           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
        (kind, source, occurred_at, detected_at, effective_at, summary, db.Jsonb(details)))
    from .tracing import jsonable
    out = jsonable(row)
    publish("security", out)
    return out


class PermissionSync:
    def __init__(self):
        self.admin = KeycloakAdmin()
        self.source = KeycloakEventSource(self.admin, since_ms=int(time.time() * 1000))
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.last_poll: float | None = None
        self.last_error: str | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name="permission-sync", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        interval = float(settings()["access"]["event_poll_seconds"])
        while not self._stop.is_set():
            try:
                self.poll_once()
                self.last_error = None
            except Exception as e:  # noqa: BLE001
                self.last_error = f"{type(e).__name__}: {e}"
                log.warning("poll lỗi: %s", self.last_error)
            self._stop.wait(interval)

    def poll_once(self) -> int:
        events = self.source.poll()
        self.last_poll = time.time()
        for ev in events:
            detected = _now()
            if ev.affects_all:
                n = access.invalidate_all()
                users = ["*"]
            else:
                n = sum(access.invalidate(u) for u in ev.user_ids)
                users = ev.user_ids
            names = []
            for u in users:
                if u == "*":
                    names.append("(tất cả)")
                    continue
                try:
                    names.append(self.admin.request("GET", f"/users/{u}").json().get("username", u))
                except Exception:  # noqa: BLE001
                    names.append(u)
            record_event("permission_change", "keycloak", ev.occurred_at, detected, _now(),
                         f"{ev.summary} -> tính lại signature: {', '.join(names)}",
                         {"kind": ev.kind, "user_ids": users, "usernames": names,
                          "signatures_invalidated": n, "operation": ev.raw.get("operationType"),
                          "representation": ev.raw.get("representation")})
        return len(events)


def publish_document_version(doc_id: str, version: int, actor: str) -> dict:
    occurred = _now()
    old = documents.current_version(doc_id)
    n_chunks = documents.ingest(doc_id, version)
    removed = cache.invalidate_doc(doc_id)
    return record_event("doc_update", "admin_api", occurred, _now(), _now(),
                        f"{doc_id}: v{old} -> v{version} ({n_chunks} chunk), xoá {len(removed)} cache entry",
                        {"doc_id": doc_id, "from_version": old, "to_version": version, "chunks": n_chunks,
                         "invalidated_entries": removed, "actor": actor})
