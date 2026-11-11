# Kiểm thử

Có 3 tầng test, cộng phần thử tay.

| Tầng | Lệnh | Cần gì đang chạy | Thời gian |
|---|---|---|---|
| Unit test | `make test` | không cần gì | khoảng 1 giây |
| Smoke test qua API | `make smoke` | hạ tầng + backend | khoảng 30 giây |
| E2E Playwright (7 kịch bản) | `make e2e` | hạ tầng + backend + frontend | khoảng 40 giây |

Smoke và E2E **gọi API thật** (Gemini, OpenAI, Keycloak) và **tự khôi phục trạng thái demo** trước và sau khi chạy. Mỗi lần chạy tốn vài nghìn token, chi phí không đáng kể.

## 1. Unit test (`tests/test_units.py`)
Kiểm tra: chunk không vượt ranh giới tài liệu và có version; fact cùng điều kiện nằm chung một chunk; classifier (NORMAL/SHORT_TTL/NO_CACHE/BYPASS); entity phân biệt gói Bạc/Vàng; signature không phụ thuộc thứ tự; prompt báo lỗi khi thiếu biến; phát hiện canary; khử trùng admin event không có `id`.

## 2. Smoke test (`scripts/smoke_api.py`)
Lấy token thật của từng user bằng password grant, rồi chạy 8 bước tương ứng các kịch bản dưới đây. Mỗi bước in PASS/FAIL kèm câu trả lời, similarity và độ trễ.

## 3. Playwright (`frontend/e2e/flow.spec.ts`)
Mỗi user một browser context riêng, đăng nhập qua form Keycloak thật.
```bash
make e2e-install     # 1 lần: tải Chromium
make e2e
# xem báo cáo HTML: cd frontend && npx playwright show-report
```
Chụp lại màn hình cho tài liệu: `make screenshots` (lưu vào `docs/screenshots/`).

## 4. Thử tay: 7 kịch bản luồng hoàn chỉnh
Mở 2 cửa sổ tách phiên: **A** = Chat, **B** = Console (`admin_ops`). Trước khi bắt đầu, vào B → Quản trị → *Khôi phục dữ liệu demo*.

| # | Làm gì | Kỳ vọng |
|---|---|---|
| 1 | A đăng nhập `cskh1`, hỏi *"Khách VIP được đổi trả trong bao lâu?"* | Trả lời 33 ngày (và 47 ngày ngoại lệ), có trích dẫn, nhãn **Sinh mới**. B → Request: dòng mới **MISS**, có token, chi phí |
| 2 | A đăng xuất, đăng nhập `cskh2`, hỏi *"Thời hạn đổi trả hàng cho khách VIP là bao lâu?"* | Nhãn **Từ cache**, khoảng vài chục ms. B → bấm vào request: bước *Tra cache* có ứng viên "thoả mọi điều kiện", similarity khoảng 0.85 |
| 3 | A đăng nhập `khach`, hỏi lại câu ở bước 1 | **Không** phải "Từ cache" (khác partition); trả lời 7 ngày, **không** có 33/47 ngày |
| 4 | B → Quản trị → bấm `cskh_agent` của `cskh1` (thu hồi). Đợi khoảng 3 giây. A đăng nhập `cskh1`, hỏi câu bước 2 | Không còn 33/47 ngày. Sidebar Chat của `cskh1` chỉ còn *Công khai, Nội bộ chung*. B → Bảo mật: có sự kiện *Đổi quyền*, "có hiệu lực sau" khoảng 1–2 giây |
| 5 | A (`khach`) hỏi *"Chính sách đổi trả cho phép trả hàng trong mấy ngày?"* rồi *"…trong bao nhiêu ngày?"* (lần 2 là HIT). B → Quản trị → *Xuất bản v2* của `return_policy`. A hỏi lại | Sau khi xuất bản: **Sinh mới**, trả lời **15 ngày**. B → Bảo mật: sự kiện *Sửa tài liệu* ghi số entry bị xoá |
| 6 | A hỏi *"Đơn hàng của tôi đang ở đâu rồi?"* rồi *"Thế còn hàng điện tử thì sao?"* | Nhãn **Không cache** và **Không dùng cache**. B → chi tiết request: bước *Quyết định lưu cache* = Không, kèm lý do |
| 7 | B → Tổng quan | Hit rate, token tiết kiệm có số liệu; **Trả lời vượt quyền = 0** (xanh). `khach` mở `/console` thì thấy trang "Bạn không có quyền vào Console" |

Thử thêm (chưa có test tự động):
- Hard negative: `khach` hỏi giá gói Bạc rồi giá gói Vàng. Câu thứ 2 phải **Sinh mới**, và Request detail ghi "entity khác".
- ABAC: `sales_bac` hỏi *"Chiết khấu cho đại lý cấp 1 miền Bắc là bao nhiêu?"* (12,5%), `sales_nam` hỏi câu tương tự thì không thấy số của miền Bắc.
- Đổi quyền ngay trong Keycloak admin console (không qua Console của app). Sự kiện vẫn xuất hiện ở trang Bảo mật, vì app đọc admin events của Keycloak.

## 5. Bộ test đầy đủ (Giai đoạn B, chưa làm)
Xem [STATUS.md](STATUS.md), mục "Chưa làm".
