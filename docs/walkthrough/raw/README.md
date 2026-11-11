# Bản ghi lời gọi hàm (tự sinh bởi trace_calls.py)

Thời điểm: 2026-11-11 04:40:53. `▶` = vào hàm, `in` = tham số, `out` = giá trị trả về, thụt lề = hàm con. Hàm tiện ích có thể đã bị ẩn (HIDE/FOLD).

- [00_startup](00_startup.md): Khởi động / import (97 lời gọi)
- [01_me](01_me.md): GET /api/me của cskh1 (lần đầu: tính access signature) (16 lời gọi)
- [02_chat_miss](02_chat_miss.md): cskh1 hỏi lần đầu: 'Khách VIP được đổi trả trong bao lâu?' → MISS (302 lời gọi)
- [03_chat_hit](03_chat_hit.md): cskh1 hỏi tiếp trong cùng session: 'Thời hạn đổi trả hàng cho khách VIP là bao lâu?' → HIT (102 lời gọi)
- [04_other_partition](04_other_partition.md): khach (chỉ đọc public) hỏi 'Khách VIP được đổi trả trong bao lâu?' → MISS ở partition khác (130 lời gọi)
- [05_no_cache](05_no_cache.md): khach hỏi câu cá nhân 'Đơn hàng của tôi đang ở đâu rồi?' → NO_CACHE (105 lời gọi)
- [06_revoke](06_revoke.md): Console: admin_ops thu hồi role cskh_agent của cskh1 → Keycloak admin event → poller (47 lời gọi)
- [07_after_revoke](07_after_revoke.md): cskh1 hỏi lại 'Thời hạn đổi trả hàng cho khách VIP là bao lâu?' sau khi bị thu hồi quyền (144 lời gọi)
- [08_publish](08_publish.md): Console: xuất bản return_policy v2 → nạp lại tài liệu, xoá cache entry liên quan (113 lời gọi)
- [09_metrics](09_metrics.md): Console: GET /api/console/metrics/overview (29 lời gọi)
- [10_reset](10_reset.md): Console: khôi phục dữ liệu demo (172 lời gọi)
