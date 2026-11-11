# Đặc tả yêu cầu

## 1. Giới thiệu

Tài liệu này đặc tả các yêu cầu chức năng và phi chức năng của hệ thống **Permission-Aware Semantic Cache**: một hệ thống hỏi đáp tài liệu nội bộ tiếng Việt, có semantic cache an toàn với phân quyền.

**Phạm vi**

- Hỏi đáp RAG có trích dẫn trên kho tài liệu có phân quyền theo collection.
- Semantic cache phân vùng theo access signature, có kiểm tra thực thể, phiên bản và TTL.
- Đồng bộ thay đổi quyền từ Keycloak và huỷ cache theo phiên bản tài liệu.
- Console giám sát, quản trị quyền và tài liệu, audit rò rỉ.

**Ngoài phạm vi (phiên bản hiện tại)**

- Cache cho hội thoại nhiều lượt: câu hỏi nối tiếp chỉ được BYPASS.
- Phân quyền đến từng tài liệu (hiện là theo collection).
- Adapter GCP/AWS thật (mới có khung).
- Upload tài liệu mới từ giao diện (tài liệu nằm trong `data/pilot/docs/`).

---

## 2. Tác nhân

| Tác nhân | Mô tả |
|---|---|
| Người dùng | Nhân viên hoặc khách hàng, hỏi đáp trên tài liệu được phép đọc. |
| Quản trị vận hành | Người có vai trò `ops_admin`, dùng Console để giám sát và quản trị. |
| Keycloak | IAM: xác thực (OIDC), quyết định quyền (Authorization Services), sinh admin events. |
| OpenAI | Tạo embedding cho câu hỏi và đoạn tài liệu. |
| Gemini | Sinh câu trả lời có trích dẫn. |
| Bộ hẹn giờ đồng bộ | Luồng nền đọc thay đổi quyền mỗi 2 giây. |

---

## 3. Yêu cầu chức năng

### FR-01 - Đăng nhập và xác định quyền
Hệ thống phải xác thực người dùng qua Keycloak và xác định tập collection người dùng được đọc.

- **Đầu vào:** access token (Bearer) do Keycloak cấp cho client `semcache-frontend`.
- **Xử lý:** kiểm tra chữ ký RS256 qua JWKS, issuer và `azp`; gọi `policy/evaluate` để lấy các collection có quyết định PERMIT; tính signature và lưu vào Redis với TTL 300 giây.
- **Đầu ra:** `user_id`, `username`, `roles`, `is_console`, `signature`, `collections`.

---

### FR-02 - Đặt câu hỏi và nhận câu trả lời có trích dẫn
Hệ thống phải trả lời câu hỏi chỉ dựa trên tài liệu người dùng được phép đọc.

- **Đầu vào:** `message` (1–2000 ký tự), `session_id` (tuỳ chọn).
- **Xử lý:** chạy pipeline 8 bước (FR-03 đến FR-07).
- **Đầu ra:** `answer`, `citations[]` (doc_id, title, section, collection, version), `status` ∈ {HIT, MISS, BYPASS, NO_CACHE}, `latency_ms`, `similarity`, `policy`.

---

### FR-03 - Phân loại chính sách cache
Hệ thống phải phân loại mỗi câu hỏi trước khi tra cache.

- **Đầu vào:** câu hỏi và embedding của câu hỏi.
- **Xử lý:** so khớp từ khoá theo `configs/classifier.yaml`; chọn intent theo độ gần với tâm của các câu mẫu; trích xuất thực thể bằng luật.
- **Đầu ra:** `policy` (NORMAL | SHORT_TTL | NO_CACHE | BYPASS), `intent`, `entities`.

---

### FR-04 - Tra semantic cache theo partition
Hệ thống chỉ được trả lời từ cache khi entry thoả **cả 6** điều kiện:

| # | Điều kiện | Lý do |
|---|---|---|
| 1 | `partition == signature` của người hỏi | Không rò rỉ thông tin, không trả lời thiếu |
| 2 | similarity ≥ ngưỡng của intent (mặc định 0,75) | Câu hỏi đủ giống |
| 3 | `entities` trùng nhau | Tránh trúng cache sai, ví dụ gói Bạc / gói Vàng |
| 4 | `prompt_version` trùng | Đổi prompt thì không dùng lại câu trả lời cũ |
| 5 | Mọi tài liệu trong provenance vẫn ở phiên bản hiện tại | Tài liệu đổi thì không trả nội dung cũ |
| 6 | Còn TTL và IAM xác nhận lại các collection trong provenance | Phòng khi bỏ lỡ sự kiện thu hồi quyền |

- **Đầu ra:** entry trúng cache (nếu có) và danh sách ứng viên kèm lý do đạt hoặc trượt (ghi vào trace).

---

### FR-05 - Truy xuất có lọc trước và IAM kiểm tra sau
Khi không trúng cache, hệ thống phải truy xuất trong phạm vi quyền và kiểm tra lại với IAM.

- **Xử lý:** Qdrant `chunks`, `filter collection ∈ signature.collections`, top-k = 5, `min_score` = 0,25. Sau đó Keycloak kiểm tra quyền với các collection của đoạn tài liệu tìm được; đoạn bị từ chối thì bị loại. Nếu IAM lỗi thì từ chối.

---

### FR-06 - Sinh câu trả lời
- **Xử lý:** Gemini với prompt `rag_answer` trong `configs/prompts.yaml`; các đoạn ngữ cảnh được gắn nhãn `[c1]..[cN]`; trích dẫn được ánh xạ ngược về tài liệu.
- Nếu không có ngữ cảnh phù hợp, trả câu "không tìm thấy" và không gọi LLM.

---

### FR-07 - Lưu câu trả lời vào cache
Hệ thống chỉ lưu câu trả lời khi: chính sách là NORMAL hoặc SHORT_TTL, có ngữ cảnh, không phải câu "không tìm thấy", và có ít nhất một trích dẫn hợp lệ.

- **Dữ liệu lưu:** vector câu hỏi (Qdrant `semantic_cache`), entry (Redis, có TTL), provenance, reverse index `cache:doc:<doc_id>`, LRU `cache:lru`.
- Khi số entry vượt `max_entries` (5000), hệ thống loại entry theo LRU.

---

### FR-08 - Lịch sử hội thoại và đánh giá
- Người dùng xem, xoá các phiên của mình. Truy cập phiên của người khác trả `404`.
- Người dùng đánh giá câu trả lời (`-1`, `0`, `1`). Đánh giá được ghi vào cả tin nhắn lẫn trace, dùng để tính tỷ lệ trúng cache sai theo phản hồi.

---

### FR-09 - Đồng bộ thay đổi quyền
- Cứ 2 giây hệ thống đọc admin events của Keycloak và loại sự kiện trùng.
- Sự kiện liên quan đến người dùng: xoá signature của người đó. Sự kiện thay đổi policy/resource: xoá signature của mọi người.
- Ghi `security_events` với `occurred_at`, `detected_at`, `effective_at`.

---

### FR-10 - Xuất bản phiên bản tài liệu
- **Đầu vào:** `doc_id`, `version`.
- **Xử lý:** chia đoạn (tối đa 400 token, chồng lấn 50 token), tạo embedding, thay các đoạn cũ trong Qdrant, cập nhật `doc:version`, xoá các entry qua reverse index.
- **Đầu ra:** sự kiện `doc_update` gồm số đoạn và danh sách entry đã xoá.

---

### FR-11 - Console giám sát
- Chỉ số tổng quan: tỷ lệ trúng cache, token và chi phí tiết kiệm, độ trễ p50/p95 theo loại request, số câu trả lời vượt quyền, thời gian thu hồi quyền có hiệu lực (trung bình và lớn nhất), thống kê theo intent.
- Danh sách request (lọc theo trạng thái, người hỏi), chi tiết từng span.
- Nội dung cache, partition và người dùng thuộc mỗi partition; xoá toàn bộ cache.
- Sự kiện bảo mật; các request bị audit đánh dấu vượt quyền.
- Cập nhật theo thời gian thực qua SSE.

---

### FR-12 - Quản trị quyền
- Xem vai trò, thuộc tính và các collection mỗi người đọc được (đánh giá trực tiếp từ Keycloak).
- Cấp hoặc thu hồi vai trò qua Admin API. Không cho quản trị viên tự thu hồi `ops_admin` của chính mình.

---

### FR-13 - Audit rò rỉ bằng canary
- Sau mỗi câu trả lời, một tác vụ nền tìm các chuỗi canary (`data/pilot/canaries.yaml`) trong câu trả lời.
- Nếu tìm thấy canary thuộc collection mà người hỏi không có quyền, trace bị đánh dấu `unauthorized = true`.

---

### FR-14 - Khôi phục dữ liệu demo
- Đưa vai trò về theo `acl.yaml`, tài liệu về phiên bản đầu, xoá cache và signature; tuỳ chọn xoá lịch sử.

---

## 4. Yêu cầu phi chức năng

### NFR-01 - Bảo mật
- Số câu trả lời vượt quyền phải bằng 0 (kiểm bằng canary).
- Lỗi IAM thì từ chối truy cập (fail-closed).
- Lịch sử hội thoại chỉ chủ phiên được xem.
- API Console kiểm tra vai trò `ops_admin` ở backend, không chỉ ở giao diện.
- API key nằm trong `.env`, không đưa vào mã nguồn.

### NFR-02 - Hiệu năng
- Trả lời từ cache phải nhanh hơn đáng kể so với sinh mới. Đo trên dữ liệu pilot: HIT p50 khoảng 20 ms, MISS p50 khoảng 1,2–1,8 giây.
- Thay đổi quyền phải có hiệu lực trong vài giây (đo được 0,3–1,9 giây với chu kỳ 2 giây).

### NFR-03 - Khả năng giải thích
- Mọi quyết định HIT/MISS phải ghi lại lý do, bao gồm từng ứng viên trượt ở điều kiện nào.

### NFR-04 - Khả năng mở rộng
- Thêm IAM khác (GCP, AWS) chỉ cần viết adapter mới theo `AccessControlBase`, không đổi cấu trúc cache. Collection được gắn namespace (`keycloak:public`, `gcp:bucket-3`).
- Đổi cách tính signature thì tăng `signature_scheme_version`; các partition cũ tự động không còn được dùng.

### NFR-05 - Khả năng cấu hình
- Prompt, ngưỡng, TTL, từ khoá phân loại, chu kỳ đồng bộ nằm trong `configs/*.yaml`, không nằm trong mã nguồn.

### NFR-06 - Khả năng tái lập
- Toàn bộ hạ tầng và ứng dụng chạy bằng Docker Compose với phiên bản cố định.
- Realm Keycloak được tạo tự động từ `acl.yaml`.

---

## 5. Ràng buộc và giả định

- Quyền đồng nhất trong mỗi collection: ai đọc được một tài liệu trong collection thì đọc được cả collection.
- Dữ liệu tiếng Việt; embedding `text-embedding-3-small` (1536 chiều).
- Một tiến trình backend; luồng đồng bộ chạy trong cùng tiến trình.
