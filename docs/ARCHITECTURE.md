# Kiến trúc

## Thành phần
```
Trình duyệt ──OIDC──► Keycloak (realm semcache: user, role, attribute, resource=collection, policy)
   │                        ▲            ▲ admin events (poll 2 s)
   │ Bearer token           │ evaluate   │
   ▼                        │            │
FastAPI backend ────────────┴────────────┘
   ├─ Qdrant: collection "chunks" (tài liệu), "semantic_cache" (vector câu hỏi đã cache)
   ├─ Redis: cache entry, reverse index, LRU, signature, cache embedding, pub/sub realtime
   ├─ Postgres: documents, sessions, messages, traces, security_events
   ├─ OpenAI: embedding
   └─ Gemini: sinh câu trả lời
```

## Luồng một câu hỏi (`backend/app/pipeline.py`)
Mỗi bước là một span trong trace và hiển thị trên Console → chi tiết request.

1. **Danh tính & signature:** lấy signature từ Redis. Nếu chưa có hoặc đã bị xoá thì hỏi Keycloak tập collection user đọc được, rồi tính `hash(scheme_version, sorted("keycloak:<collection>"))`.
2. **Embedding** câu hỏi (OpenAI, có cache theo nội dung).
3. **Phân loại** (rule): NORMAL / SHORT_TTL / NO_CACHE / BYPASS, intent, entity.
4. **Tra cache** (nếu NORMAL hoặc SHORT_TTL): Qdrant tìm trong `semantic_cache` **có lọc partition = signature**, lấy 3 ứng viên, kiểm tra lần lượt:
   1. similarity ≥ ngưỡng của intent
   2. entity giống nhau
   3. version prompt `rag_answer` giống nhau
   4. version mọi tài liệu trong provenance vẫn là version hiện tại
   5. chưa hết TTL
   6. IAM re-verify các collection trong provenance (bật/tắt trong settings)

   Ứng viên đầu tiên thoả hết thì HIT. Nếu IAM re-verify từ chối thì xoá signature để tính lại.
5. **Retrieval:** Qdrant `chunks`, filter `collection ∈ signature.collections`, top-k = 5.
6. **IAM post-verify:** hỏi Keycloak quyền các collection của chunk lấy được; chunk bị từ chối thì loại.
7. **LLM:** Gemini với prompt `rag_answer`; context đánh nhãn `[c1]..[cN]`.
8. **Admission:** lưu cache nếu cacheable, có ngữ cảnh, không phải câu "không tìm thấy", có trích dẫn hợp lệ. Entry ghi provenance = mọi chunk đưa vào context.
9. Sau khi trả lời: lưu trace, phát SSE; **audit canary** chạy nền.

## Vì sao an toàn
- Partition = signature, nên hai user dùng chung entry chỉ khi đọc được **đúng cùng** tập collection. Nhờ vậy không rò rỉ và không trả lời thiếu.
- Khi quyền đổi, Keycloak ghi admin event. Poller xoá signature của user bị ảnh hưởng, nên request sau tính lại signature và rơi vào partition mới.
- Nếu lỡ event: signature hết hạn sau `signature_ttl_seconds`, và trong lúc đó IAM re-verify khi hit vẫn chặn.
- Retrieval lọc theo snapshot nhưng IAM post-verify mới là trọng tài cuối. Snapshot rộng hơn thực tế thì bị IAM chặn; snapshot hẹp hơn chỉ làm thiếu tài liệu tạm thời.
- Lỗi IAM thì từ chối (fail-closed).

## Mô hình dữ liệu chính
**Cache entry** (Redis `cache:entry:<id>`, vector ở Qdrant `semantic_cache`):
`entry_id, partition, question, answer, citations[], provenance[{chunk_id, doc_id, version, collection}], intent, entities, policy, prompt_version, model, created_at, ttl, gen_tokens_in/out, gen_cost_usd, hits, last_hit`

**Redis khác:** `cache:doc:<doc_id>` (set entry), `cache:lru` (zset), `sig:user:<user_id>` (signature, TTL), `doc:version` (hash), `emb:<model>:<sha1>` (embedding).

**Postgres:** `documents`, `sessions`, `messages`, `traces` (spans JSONB, audit JSONB), `security_events` (occurred/detected/effective_at).

## Mở rộng sang IAM khác
Cache không chứa thông tin policy; mọi khác biệt nằm trong adapter:
```python
class AccessControlBase:
    namespace: str
    def list_accessible_collections(user) -> set[str]
    def check_collections(user, collections) -> dict[str, bool]
class ChangeEventSource:
    def poll() -> list[AccessChangeEvent]
```
Collection id được gắn namespace khi tính signature (`keycloak:public`, `gcp:bucket-3`). Đổi cách tính signature thì tăng `signature_scheme_version`: mọi partition cũ thành MISS, không cần migrate entry. Xem `backend/app/iam/stubs.py` cho GCP/AWS.

## API
| Method | Path | Quyền |
|---|---|---|
| GET | `/api/health` | – |
| GET | `/api/me` | đăng nhập |
| POST | `/api/chat` | đăng nhập |
| GET/DELETE | `/api/sessions`, `/api/sessions/{id}/messages`, `/api/sessions/{id}` | chủ session |
| POST | `/api/messages/{id}/feedback` | chủ session |
| GET | `/api/console/metrics/overview`, `/traces`, `/traces/{id}`, `/cache/entries`, `/security/events` | ops_admin |
| DELETE | `/api/console/cache` | ops_admin |
| GET | `/api/console/stream?token=` (SSE) | ops_admin |
| GET/POST | `/api/console/admin/users`, `/users/{u}/roles`, `/documents`, `/documents/{id}/publish`, `/reset` | ops_admin |
