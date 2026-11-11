"""Smoke test luồng hoàn chỉnh qua API thật (không cần trình duyệt). Cần backend đang chạy ở :8000.
    .venv/bin/python scripts/smoke_api.py
In ra kết quả từng bước; thoát mã 1 nếu có bước sai.
"""
from __future__ import annotations

import re
import sys
import time

import httpx

API = "http://localhost:8000/api"
KC = "http://localhost:8080/realms/semcache/protocol/openid-connect/token"
PASSWORD = "demo1234"
FAILS: list[str] = []


def token(username: str) -> str:
    r = httpx.post(KC, data={"grant_type": "password", "client_id": "semcache-frontend",
                             "username": username, "password": PASSWORD})
    r.raise_for_status()
    return r.json()["access_token"]


class U:
    def __init__(self, username: str):
        self.name = username
        self.h = {"Authorization": f"Bearer {token(username)}"}

    def ask(self, q: str, session_id: str | None = None) -> dict:
        r = httpx.post(f"{API}/chat", json={"message": q, "session_id": session_id}, headers=self.h, timeout=90)
        r.raise_for_status()
        return r.json()

    def get(self, path: str):
        r = httpx.get(f"{API}{path}", headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def post(self, path: str, body: dict):
        r = httpx.post(f"{API}{path}", json=body, headers=self.h, timeout=120)
        r.raise_for_status()
        return r.json()


def check(name: str, cond: bool, info: str = "") -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {info}")
    if not cond:
        FAILS.append(name)


def show(u: U, q: str, res: dict) -> None:
    sim = res.get("similarity")
    print(f"- {u.name}: {q}\n    -> {res['status']} sim={sim if sim is None else round(sim, 3)} "
          f"{res['latency_ms']:.0f}ms | {res['answer'][:140]!r}")


def main() -> int:
    admin = U("admin_ops")
    admin.post("/console/admin/reset", {"clear_history": False})
    cskh1, cskh2, khach = U("cskh1"), U("cskh2"), U("khach")

    print("\n1. Hỏi lần đầu -> MISS")
    q1 = "Khách VIP được đổi trả trong bao lâu?"
    r = cskh1.ask(q1); show(cskh1, q1, r)
    check("MISS lần đầu", r["status"] == "MISS")
    check("có thông tin VIP (33 ngày)", "33" in r["answer"])

    print("\n2. Diễn đạt khác, user khác cùng quyền -> HIT")
    q2 = "Thời hạn đổi trả hàng cho khách VIP là bao lâu?"
    r = cskh2.ask(q2); show(cskh2, q2, r)
    check("HIT cùng partition", r["status"] == "HIT")

    print("\n3. User public hỏi cùng câu -> không hit chéo, không lộ canary")
    r = khach.ask(q1); show(khach, q1, r)
    check("không HIT chéo partition", r["status"] != "HIT")
    check("không chứa canary 33/47 ngày", not re.search(r"\b(33|47)\s*ngày", r["answer"]))

    print("\n4. Hard negative: gói Bạc vs gói Vàng")
    r = khach.ask("Giá gói bảo hành mở rộng Bạc là bao nhiêu?"); show(khach, "Bạc", r)
    r2 = khach.ask("Giá gói bảo hành mở rộng Vàng là bao nhiêu?"); show(khach, "Vàng", r2)
    check("gói Vàng không HIT entry gói Bạc", r2["status"] != "HIT" and "890" in r2["answer"])

    print("\n5. Thu hồi quyền cskh của cskh1")
    admin.post("/console/admin/users/cskh1/roles", {"role": "cskh_agent", "grant": False})
    time.sleep(4)   # > chu kỳ poll admin-events
    r = cskh1.ask(q2); show(cskh1, q2, r)
    check("sau thu hồi không lộ canary", not re.search(r"\b(33|47)\s*ngày", r["answer"]))
    ev = admin.get("/console/security/events")["events"]
    pe = [e for e in ev if e["kind"] == "permission_change"]
    check("có security event thu hồi quyền", bool(pe),
          f"window={pe[0].get('window_seconds'):.2f}s" if pe else "")
    admin.post("/console/admin/users/cskh1/roles", {"role": "cskh_agent", "grant": True})

    print("\n6. Sửa tài liệu: đổi trả 7 -> 15 ngày")
    q3 = "Chính sách đổi trả cho phép trả hàng trong mấy ngày?"
    r = khach.ask(q3); show(khach, q3, r)
    q3b = "Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?"
    r = khach.ask(q3b); show(khach, "paraphrase", r)
    check("paraphrase HIT trước khi sửa", r["status"] == "HIT")
    ev = admin.post("/console/admin/documents/return_policy/publish", {"version": 2}); print("   ", ev["summary"])
    r = khach.ask(q3b); show(khach, "sau sửa", r)
    check("sau sửa MISS và trả lời 15 ngày", r["status"] == "MISS" and "15" in r["answer"])

    print("\n7. Bypass")
    r = khach.ask("Đơn hàng của tôi đang ở đâu rồi?"); show(khach, "cá nhân", r)
    check("câu cá nhân NO_CACHE", r["status"] == "NO_CACHE")
    r = khach.ask("Thế còn hàng điện tử thì sao?", r["session_id"]); show(khach, "nối tiếp", r)
    check("câu nối tiếp BYPASS", r["status"] == "BYPASS")

    print("\n8. Console")
    time.sleep(1)
    ov = admin.get("/console/metrics/overview")
    t = ov["totals"]
    print(f"   requests={t['requests']} hits={t['hits']} misses={t['misses']} hit_rate={ov['hit_rate']}"
          f" unauthorized={t['unauthorized']} audited={t['audited']} saved_tokens={t['saved_tokens']}")
    check("unauthorized = 0", t["unauthorized"] == 0)
    try:
        U("khach").get("/console/metrics/overview")
        check("user thường bị chặn Console", False)
    except httpx.HTTPStatusError as e:
        check("user thường bị chặn Console (403)", e.response.status_code == 403)

    admin.post("/console/admin/reset", {"clear_history": False})
    print(f"\n{'TẤT CẢ PASS' if not FAILS else 'FAIL: ' + ', '.join(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
