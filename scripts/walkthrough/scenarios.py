"""Kịch bản ghi lời gọi hàm cho backend semantic-cache (dùng với trace_calls.py của skill walkthrough).

    make trace
    # = .venv/bin/python scripts/walkthrough/trace_calls.py --src backend/app \
    #     --scenarios scripts/walkthrough/scenarios.py --out docs/walkthrough/raw

Cần: hạ tầng đang chạy (make infra-up), đã make setup, .env có key OpenAI/Gemini. Gọi API thật (vài nghìn token).
"""
from __future__ import annotations

import os
import time

# Ẩn hẳn (cả cây con): hàm tiện ích không mang thông tin luồng
HIDE = {"config._expand", "config.settings", "config.env", "config.data_dir", "embeddings.model", "embeddings._key",
        "access._key", "db.pool", "db.conn", "prompts._all", "tracing.Trace.span", "tracing.Trace.set",
        "tracing.Trace.elapsed_ms", "auth.issuer", "auth._jwks", "chunking._enc", "llm.model", "tracing.jsonable"}
HIDE_PREFIX = ("clients.",)
FOLD = {"config.load_yaml", "chunking.ntokens"}
TRANSPARENT = {"sync.PermissionSync._run"}          # vòng lặp thread đồng bộ quyền, không bao giờ return


def NOISE(n: dict) -> bool:
    # các lần poll admin-events không có sự kiện nào
    return n["name"] == "sync.PermissionSync.poll_once" and n.get("result") == "0"


SUMMARIZERS = {
    "Trace": lambda v: f"Trace(id={v.id!r}, status={v.fields.get('status')!r}, {len(v.spans)} span)",
}

Q1 = "Khách VIP được đổi trả trong bao lâu?"
Q2 = "Thời hạn đổi trả hàng cho khách VIP là bao lâu?"
Q_RET = "Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?"


def run(trace) -> None:
    import httpx
    from fastapi.testclient import TestClient

    from app.clients import rds
    from app.main import app

    trace.off()
    if not os.environ.get("KEEP_EMBEDDINGS"):            # xoá cache embedding để thấy lời gọi OpenAI thật
        keys = list(rds().scan_iter("emb:*"))
        if keys:
            rds().delete(*keys)

    def token(u: str) -> dict:
        r = httpx.post("http://localhost:8080/realms/semcache/protocol/openid-connect/token",
                       data={"grant_type": "password", "client_id": "semcache-frontend", "username": u,
                             "password": "demo1234"})
        r.raise_for_status()
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    trace.rec.enabled = True                              # ghi phần khởi động (lifespan) vào nhãn 00_startup
    with TestClient(app) as client:
        trace.off()
        H = {u: token(u) for u in ("cskh1", "khach", "admin_ops")}
        client.post("/api/console/admin/reset", json={"clear_history": False}, headers=H["admin_ops"])
        time.sleep(4)                                     # để poller xử lý xong event của reset

        trace("01_me", "GET /api/me của cskh1 (lần đầu: tính access signature)",
              lambda: client.get("/api/me", headers=H["cskh1"]).json())
        r1 = trace("02_chat_miss", f"cskh1 hỏi lần đầu: '{Q1}' → MISS",
                   lambda: client.post("/api/chat", json={"message": Q1}, headers=H["cskh1"]).json(), wait=1.5)
        trace("03_chat_hit", f"cskh1 hỏi tiếp trong cùng session: '{Q2}' → HIT",
              lambda: client.post("/api/chat", json={"message": Q2, "session_id": r1["session_id"]},
                                  headers=H["cskh1"]).json(), wait=1.5)
        trace("04_other_partition", f"khach (chỉ đọc public) hỏi '{Q1}' → MISS ở partition khác",
              lambda: client.post("/api/chat", json={"message": Q1}, headers=H["khach"]).json(), wait=1.5)
        trace("05_no_cache", "khach hỏi câu cá nhân 'Đơn hàng của tôi đang ở đâu rồi?' → NO_CACHE",
              lambda: client.post("/api/chat", json={"message": "Đơn hàng của tôi đang ở đâu rồi?"},
                                  headers=H["khach"]).json(), wait=1.5)
        trace("06_revoke", "Console: admin_ops thu hồi role cskh_agent của cskh1 → Keycloak admin event → poller",
              lambda: client.post("/api/console/admin/users/cskh1/roles", json={"role": "cskh_agent", "grant": False},
                                  headers=H["admin_ops"]).json(), wait=4.5)
        trace("07_after_revoke", f"cskh1 hỏi lại '{Q2}' sau khi bị thu hồi quyền",
              lambda: client.post("/api/chat", json={"message": Q2}, headers=H["cskh1"]).json(), wait=1.5)
        client.post("/api/chat", json={"message": Q_RET}, headers=H["khach"])   # tạo entry dùng return_policy
        time.sleep(1.5)
        trace("08_publish", "Console: xuất bản return_policy v2 → nạp lại tài liệu, xoá cache entry liên quan",
              lambda: client.post("/api/console/admin/documents/return_policy/publish", json={"version": 2},
                                  headers=H["admin_ops"]).json(), wait=0.5)
        trace("09_metrics", "Console: GET /api/console/metrics/overview",
              lambda: client.get("/api/console/metrics/overview", headers=H["admin_ops"]).json())
        trace("10_reset", "Console: khôi phục dữ liệu demo",
              lambda: client.post("/api/console/admin/reset", json={"clear_history": False},
                                  headers=H["admin_ops"]).json(), wait=4.5)
