# Mô tả phần mềm

## Permission-Aware Semantic Cache cho RAG tài liệu nội bộ

**Hệ thống hỏi đáp tài liệu nội bộ tiếng Việt có semantic cache nhận biết phân quyền**

---

### Tổng quan

Đây là một hệ thống hỏi đáp dựa trên tài liệu nội bộ (Retrieval-Augmented Generation, RAG). Mỗi người dùng chỉ được đọc một phần kho tài liệu, tuỳ theo vai trò và thuộc tính khai báo trong Keycloak. Hệ thống thêm một lớp **semantic cache**: khi gặp câu hỏi giống ý một câu đã hỏi, hệ thống trả lại câu trả lời cũ trong khoảng 20 ms thay vì mất trên 1 giây gọi LLM. Cache được thiết kế sao cho **không làm lộ thông tin** giữa những người có quyền khác nhau.

Đề tài mở rộng từ PermRAG (Jeong & Lee, IEEE Access 2025). Hệ thống giữ nguyên tắc "IAM gốc là trọng tài cuối cùng" của PermRAG, và bổ sung:

- cache câu trả lời LLM;
- cơ chế giữ cache đúng khi quyền hoặc tài liệu thay đổi;
- lọc theo quyền ngay khi truy xuất, thay vì lọc sau.

---

### Bài toán giải quyết

Semantic cache thông thường (ví dụ GPTCache) dùng chung cho mọi người dùng. Đặt vào môi trường có phân quyền, cách làm này gặp các vấn đề sau:

| Vấn đề | Ví dụ |
|---|---|
| **Rò rỉ thông tin** | Nhân viên CSKH hỏi "khách VIP được đổi trả bao lâu?", câu trả lời chứa quy định nội bộ (33 ngày). Khách hàng hỏi câu tương tự lại nhận đúng câu trả lời đó. |
| **Trả lời thiếu** | Người nhiều quyền nhận câu trả lời được sinh cho người ít quyền, nên thiếu thông tin. |
| **Quyền thay đổi** | Thu hồi vai trò CSKH, nhưng cache vẫn trả câu trả lời cũ có thông tin CSKH. |
| **Tài liệu thay đổi** | Chính sách đổi trả đổi từ 7 sang 10 ngày, nhưng cache vẫn trả "7 ngày". |
| **Trúng cache sai** | "Giá gói Bạc" và "giá gói Vàng" có độ tương đồng embedding 0,84, cao hơn nhiều cặp câu cùng ý. |
| **Câu hỏi cá nhân / theo thời điểm** | "Đơn hàng của tôi đâu?" không được dùng lại câu trả lời của người khác. |

PermRAG giải quyết việc kiểm tra quyền nhưng không có cache. Ngoài ra, PermRAG lọc sau khi đã lấy top-k trên toàn kho, nên người ít quyền gần như không còn ngữ cảnh để trả lời.

---

### Giải pháp kỹ thuật

**Phân vùng cache theo access signature**

- `signature = hash(scheme_version, sorted(namespace:collection được đọc))`, trong đó tập collection được tính bởi Keycloak tại thời điểm hỏi.
- Hai người dùng chỉ dùng chung câu trả lời khi đọc được **đúng cùng một** tập collection. Nhờ vậy không rò rỉ thông tin và không trả lời thiếu.
- Signature được lưu trong Redis với TTL 300 giây.

**Sáu điều kiện để trả lời từ cache**

1. Entry nằm cùng partition (cùng signature).
2. Độ tương đồng ≥ ngưỡng (mặc định 0,75, có thể đặt riêng theo intent).
3. Thực thể trong câu hỏi trùng nhau (gói Bạc ≠ gói Vàng).
4. Phiên bản prompt không đổi.
5. Mọi tài liệu trong provenance vẫn ở phiên bản hiện tại.
6. Entry còn hạn TTL, và Keycloak xác nhận lại quyền đọc các collection trong provenance.

**Giữ cache đúng khi dữ liệu thay đổi**

- **Provenance + reverse index:** mỗi câu trả lời ghi lại đoạn tài liệu và phiên bản đã dùng. Khi tài liệu có phiên bản mới, hệ thống xoá đúng các entry liên quan.
- **Đồng bộ quyền:** cứ 2 giây hệ thống đọc admin events của Keycloak một lần. Khi quyền của ai đó thay đổi, signature của người đó bị xoá và người đó chuyển sang partition mới. Thời gian đo được từ lúc thu hồi đến lúc có hiệu lực là khoảng 1–2 giây.
- **Phòng khi bỏ lỡ sự kiện:** signature có TTL, và IAM luôn kiểm tra lại khi trả lời từ cache.

**Lọc trước theo quyền, IAM kiểm tra lần cuối**

- Truy xuất trong Qdrant có bộ lọc `collection ∈ signature.collections`.
- Sau khi truy xuất, Keycloak kiểm tra lại quyền với từng collection của các đoạn tài liệu. Đoạn nào bị từ chối thì bị loại. Nếu Keycloak lỗi, hệ thống từ chối (fail-closed).

**Bộ phân loại chính sách cache (theo luật)**

- `NORMAL` (TTL 7 ngày), `SHORT_TTL` (1 giờ), `NO_CACHE` (câu hỏi cá nhân hoặc thời gian thực), `BYPASS` (câu hỏi nối tiếp, phụ thuộc lịch sử hội thoại).
- Từ khoá, intent và thực thể được khai báo trong `configs/classifier.yaml`.

**Quan sát và kiểm tra rò rỉ**

- Mỗi request được ghi thành trace gồm nhiều span: signature, embedding, phân loại, tra cache (kèm lý do của từng ứng viên), truy xuất, IAM, LLM, lưu cache.
- Hệ thống kiểm tra rò rỉ bằng canary: các tài liệu mật có cài sẵn chuỗi đặc biệt. Nếu chuỗi đó xuất hiện trong câu trả lời của người không có quyền, request bị đánh dấu là vượt quyền.

---

### Kiến trúc hệ thống

| Tầng | Công nghệ |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS 4, Recharts, keycloak-js |
| Backend | Python 3.12, FastAPI, SSE |
| IAM | Keycloak 26 (OIDC + Authorization Services) |
| Vector DB | Qdrant (đoạn tài liệu và vector câu hỏi đã cache) |
| Cache, pub/sub | Redis |
| CSDL quan hệ | PostgreSQL (phiên, trace, sự kiện bảo mật) |
| Embedding | OpenAI `text-embedding-3-small` |
| LLM | Gemini `gemini-3.5-flash-lite` |
| Triển khai | Docker Compose |

---

### Tính năng chính

**Hỏi đáp (Chat)**

- Đăng nhập qua Keycloak và hiển thị các collection người dùng được đọc.
- Câu trả lời có trích dẫn nguồn, kèm nhãn "Sinh mới" hoặc "Từ cache" và độ trễ.
- Lịch sử phiên hội thoại (chỉ chủ phiên xem được) và đánh giá 👍/👎 cho câu trả lời.

**Console vận hành** (chỉ cho vai trò `ops_admin`)

- **Tổng quan:** tỷ lệ trả lời từ cache, token và chi phí tiết kiệm, độ trễ p50/p95 theo loại request, số câu trả lời vượt quyền, thời gian thu hồi quyền có hiệu lực, thống kê theo intent.
- **Request:** danh sách request cập nhật theo thời gian thực qua SSE. Trang chi tiết hiển thị từng bước xử lý và lý do trúng hoặc trượt cache.
- **Cache:** các entry, partition và người dùng thuộc mỗi partition, provenance, TTL còn lại; có nút xoá toàn bộ cache.
- **Bảo mật:** dòng thời gian các thay đổi quyền và tài liệu (thời điểm xảy ra, phát hiện, có hiệu lực) và kết quả audit canary.
- **Quản trị:** cấp/thu hồi vai trò (ghi thẳng vào Keycloak), xuất bản phiên bản tài liệu, khôi phục dữ liệu demo.

---

### Quy mô (Giai đoạn A, dữ liệu pilot)

- 10 tài liệu tiếng Việt, chia trong 6 collection: công khai, nội bộ chung, CSKH, nhân sự (mật), kinh doanh miền Bắc, kinh doanh miền Nam. Tài liệu `return_policy` có 2 phiên bản.
- 7 người dùng, 6 vai trò; có policy theo thuộc tính (`region=north|south`).
- 18 endpoint REST và 1 luồng SSE.
- 7 kịch bản kiểm thử luồng hoàn chỉnh trên giao diện bằng Playwright, tất cả đều đạt.
