# Cấu hình

## `.env` (secret và địa chỉ hạ tầng; không commit)
| Biến | Ý nghĩa |
|---|---|
| `OPENAI_API_KEY`, `GEMINI_API_KEY` | Key API |
| `LLM_MODEL` | Mặc định `gemini-3.5-flash-lite` |
| `EMBEDDING_MODEL` | Mặc định `text-embedding-3-small` |
| `POSTGRES_*`, `QDRANT_URL`, `REDIS_URL` | Địa chỉ hạ tầng (mặc định khớp docker-compose) |
| `KEYCLOAK_URL` | Địa chỉ backend gọi Keycloak (`http://keycloak:8080` khi chạy trong Docker) |
| `KEYCLOAK_PUBLIC_URL` | Địa chỉ trình duyệt thấy, dùng để kiểm tra `iss` của token |
| `KEYCLOAK_ADMIN(_PASSWORD)` | Admin master realm, chỉ `setup_keycloak.py` dùng |
| `KEYCLOAK_BACKEND_SECRET` | Secret của client backend (mặc định giá trị dev) |

## `configs/settings.yaml`
| Khoá | Ý nghĩa | Gợi ý chỉnh |
|---|---|---|
| `chunking.max_tokens / min_tokens / overlap_tokens` | Kích thước chunk theo cấu trúc | Chốt bằng fact recall@k ở Giai đoạn B |
| `retrieval.top_k`, `min_score` | Số chunk đưa vào LLM, ngưỡng loại chunk quá xa | |
| `cache.threshold_default` | Ngưỡng similarity để hit (0.75, đo trên pilot) | Nhiều hit bị chê thì tăng; ít hit và chưa có hit sai thì giảm (Console có gợi ý theo intent) |
| `cache.threshold_by_intent` | Ngưỡng riêng từng intent | Kết quả E1 |
| `cache.ttl_seconds.NORMAL / SHORT_TTL` | TTL theo loại câu hỏi | |
| `cache.max_entries` | Vượt thì loại theo LRU | |
| `cache.reverify_iam_on_hit` | Bật điều kiện 6: kiểm IAM khi hit (thêm khoảng 40 ms) | Tắt nếu cần latency thấp và chấp nhận cửa sổ rủi ro = TTL signature |
| `access.signature_ttl_seconds` | TTL dự phòng của signature | Chặn trên thời gian dùng quyền cũ khi lỡ event |
| `access.event_poll_seconds` | Chu kỳ đọc admin events | Giảm để thu hồi quyền nhanh hơn |
| `access.signature_scheme_version` | Tăng khi đổi cách tính signature (mọi partition cũ thành MISS) | |
| `pricing.*` | USD / 1 triệu token, chỉ để ước lượng chi phí trên Console | Chỉnh theo bảng giá thật |

## `configs/prompts.yaml`
Toàn bộ prompt LLM. Code gọi `prompts.render("rag_answer", question=…, context=…, history=…, no_answer=…)`.
- Lúc khởi động, backend kiểm tra prompt chỉ dùng các biến mà code truyền; sai thì báo lỗi ngay.
- **Đổi nội dung `rag_answer` thì mã phiên bản prompt đổi, và entry cache sinh bằng prompt cũ tự động thành MISS** (điều kiện 3).
- `no_answer_text`: câu trả lời khi không có thông tin. Câu này không bao giờ được cache.

## `configs/classifier.yaml`
- `policies.NO_CACHE.keywords`: câu cá nhân, không cache.
- `policies.SHORT_TTL.keywords`: câu phụ thuộc thời điểm.
- `policies.BYPASS`: câu nối tiếp (`starts_with`, `keywords`, `min_words`).
- `intent.examples`: câu mẫu cho từng intent; `min_similarity` thấp hơn thì gán `default`.
- `entities`: từ điển entity. Câu hỏi và entry khác entity thì không hit (vd gói Bạc / gói Vàng).

## `data/pilot/`
- `docs/<doc_id>.v<N>.md`: tài liệu Markdown có front matter (`doc_id, title, collection, version`).
- `acl.yaml`: role, policy (role/regex), collection → policy, user. Sửa xong chạy `make keycloak`.
- `canaries.yaml`: regex giá trị đặc trưng của collection mật, dùng để audit rò rỉ.
- `questions.yaml`: câu hỏi pilot cho test.
