# API Reference

Base URL: `http://localhost:8000/api`
Tài liệu tương tác (OpenAPI): `http://localhost:8000/docs`
Mọi request và response dùng JSON, trừ luồng SSE.

---

## Xác thực

Mọi endpoint (trừ `/api/health`) cần access token do Keycloak cấp cho client `semcache-frontend`:

```http
Authorization: Bearer <access_token>
```

Lấy token để thử bằng `curl` (tài khoản demo, mật khẩu `demo1234`):

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/realms/semcache/protocol/openid-connect/token \
  -d grant_type=password -d client_id=semcache-frontend \
  -d username=cskh1 -d password=demo1234 | jq -r .access_token)
```

| Mã lỗi | Khi nào |
|---|---|
| `401` | Thiếu token, token sai chữ ký hoặc hết hạn, token không phải của `semcache-frontend` |
| `403` | Gọi API Console khi không có vai trò `ops_admin` |
| `404` | Không có tài nguyên, hoặc tài nguyên thuộc người khác (phiên, tin nhắn) |
| `400` / `422` | Dữ liệu vào không hợp lệ |
| `502` | Lỗi trong pipeline (LLM, IAM…); trace vẫn được lưu với `status = ERROR` |

---

## Chung

### `GET /api/health`

Kiểm tra backend và luồng đồng bộ quyền. Không cần token.

**Response `200`**

```json
{ "ok": true, "sync_last_poll": 1794371838.21, "sync_error": null }
```

---

### `GET /api/me`

Thông tin người dùng hiện tại và access signature. Lần gọi đầu tiên sẽ hỏi Keycloak để tính signature.

**Response `200`**

```json
{
  "user_id": "829671b9-5f8b-431d-9b2f-8a31158a3a2d",
  "username": "cskh1",
  "name": "Lan CSKH",
  "roles": ["default-roles-semcache", "offline_access", "uma_authorization", "employee", "cskh_agent"],
  "is_console": false,
  "signature": "95503c7831d2f7ed",
  "collections": ["cskh", "internal_all", "public"]
}
```

---

## Chat

### `POST /api/chat`

Đặt câu hỏi. Nếu không có `session_id`, hệ thống tạo phiên mới. Bốn tin nhắn gần nhất của phiên được dùng làm lịch sử.

**Request body**

| Trường | Kiểu | Mô tả |
|---|---|---|
| `message` | `string` | Câu hỏi, 1–2000 ký tự |
| `session_id` | `string \| null` | Phiên hiện có (phải thuộc người gọi) |

```json
{ "message": "Thời hạn đổi trả hàng cho khách VIP là bao lâu?", "session_id": "7808365c-6682-411c-82ba-438243673b27" }
```

**Response `200`**

| Trường | Mô tả |
|---|---|
| `status` | `HIT` (từ cache), `MISS` (sinh mới), `NO_CACHE` (câu hỏi không được cache), `BYPASS` (câu hỏi nối tiếp) |
| `similarity` | Độ tương đồng với câu hỏi trong cache (chỉ khi HIT) |
| `policy` | Chính sách cache do bộ phân loại chọn |
| `citations` | Các đoạn tài liệu được trích dẫn |
| `trace_id` | Dùng để xem chi tiết trên Console |

```json
{
  "session_id": "7808365c-6682-411c-82ba-438243673b27",
  "message_id": "5d9402b4-e581-4df7-8156-9e3b997cc2b0",
  "trace_id": "7b8f0d29-ade8-48f8-983f-64641d9b02ce",
  "status": "HIT",
  "answer": "Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến tối đa 47 ngày [c2].",
  "citations": [
    {
      "label": "c2",
      "doc_id": "vip_return_exception",
      "title": "Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP",
      "section": "Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP",
      "collection": "cskh",
      "version": 1
    }
  ],
  "latency_ms": 885.9,
  "similarity": 0.8471,
  "policy": "NORMAL"
}
```

Khi không tìm thấy thông tin trong phạm vi quyền:

```json
{ "status": "NO_CACHE", "answer": "Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.", "citations": [], "policy": "NO_CACHE", "...": "..." }
```

**Lỗi:** `404` nếu `session_id` không thuộc người gọi; `502` nếu pipeline lỗi.

---

### `GET /api/sessions`

Danh sách phiên của người gọi, mới nhất trước.

**Response `200`**

```json
[
  { "id": "7808365c-6682-411c-82ba-438243673b27", "title": "Khách VIP được đổi trả trong bao lâu?",
    "created_at": "2026-11-11T04:05:12+00:00", "updated_at": "2026-11-11T04:05:31+00:00" }
]
```

---

### `GET /api/sessions/{session_id}/messages`

Tin nhắn của một phiên. Chỉ chủ phiên được xem.

**Response `200`**

```json
[
  { "id": "…", "role": "user", "content": "Khách VIP được đổi trả trong bao lâu?", "trace_id": null,
    "cache_status": null, "citations": null, "feedback": null, "created_at": "…" },
  { "id": "d643980e-…", "role": "assistant", "content": "Khách hàng hạng VIP được đổi trả trong vòng 33 ngày…",
    "trace_id": "69867628-…", "cache_status": "MISS", "citations": [ { "label": "c2", "doc_id": "vip_return_exception", "…": "…" } ],
    "feedback": 1, "created_at": "…" }
]
```

**Lỗi:** `404` nếu phiên không tồn tại hoặc thuộc người khác.

---

### `DELETE /api/sessions/{session_id}`

Xoá phiên và các tin nhắn của phiên.

**Response `200`** `{ "ok": true }`

---

### `POST /api/messages/{message_id}/feedback`

Đánh giá câu trả lời. Đánh giá được ghi vào cả tin nhắn và trace, dùng để tính tỷ lệ trúng cache sai.

**Request body**

| Trường | Kiểu | Mô tả |
|---|---|---|
| `value` | `integer` | `1` (hữu ích), `-1` (sai), `0` (bỏ đánh giá) |

**Response `200`** `{ "ok": true }`

---

## Console (cần vai trò `ops_admin`)

### `GET /api/console/metrics/overview`

Chỉ số tổng quan trong một cửa sổ thời gian.

**Query params**

| Param | Kiểu | Mô tả |
|---|---|---|
| `minutes` | `integer` | Cửa sổ thời gian, mặc định `1440` (24 giờ) |

**Response `200`** (rút gọn)

```json
{
  "window_minutes": 1440,
  "totals": { "requests": 29, "hits": 6, "misses": 18, "bypass": 1, "no_cache": 4, "errors": 0,
              "llm_tokens": 16216, "saved_tokens": 4505, "cost_usd": 0.0019, "saved_cost_usd": 0.0005,
              "unauthorized": 0, "audited": 29, "hit_negative_feedback": 0, "hit_feedback": 0 },
  "hit_rate": 0.25,
  "false_hit_rate_feedback": null,
  "latency": {
    "HIT":  { "n": 6,  "p50": 163.0,  "p95": 1045.05 },
    "MISS": { "n": 18, "p50": 1811.5, "p95": 5782.685 }
  },
  "series": [ { "t": "2026-11-11T04:37:00+00:00", "requests": 6, "hits": 1, "misses": 4, "avg_latency": 3169.43 } ],
  "by_intent": [ { "intent": "return_policy", "requests": 24, "hits": 6, "misses": 18,
                   "hit_negative_feedback": 0, "avg_hit_similarity": 0.8576 } ],
  "cache": { "entries": 7, "...": "..." },
  "partitions": { "95503c7831d2f7ed": ["cskh1", "cskh2"] },
  "revocation": { "n": 2, "avg_s": 1.24, "max_s": 1.35 }
}
```

`hit_rate` = HIT / (HIT + MISS). Các request `NO_CACHE` và `BYPASS` không được tính vào.

---

### `GET /api/console/traces`

Danh sách request gần đây.

**Query params**

| Param | Kiểu | Mô tả |
|---|---|---|
| `limit` | `integer` | Mặc định `100` |
| `status` | `string` | `HIT`, `MISS`, `BYPASS`, `NO_CACHE`, `ERROR` |
| `username` | `string` | Lọc theo người hỏi |

**Response `200`**

```json
[
  { "id": "7b8f0d29-…", "created_at": "…", "username": "cskh1",
    "question": "Thời hạn đổi trả hàng cho khách VIP là bao lâu?", "status": "HIT", "policy": "NORMAL",
    "intent": "return_policy", "partition": "95503c7831d2f7ed", "similarity": 0.8471, "latency_ms": 19.0,
    "llm_tokens_in": 0, "llm_tokens_out": 0, "cost_usd": 0.0, "saved_tokens": 769, "saved_cost_usd": 0.00009,
    "unauthorized": false, "feedback": null }
]
```

---

### `GET /api/console/traces/{trace_id}`

Toàn bộ một trace, gồm `spans` (các bước xử lý) và `audit`. Tên span: `identity`, `embed`, `classify`, `cache_lookup`, `cache_hit`, `retrieval`, `iam_verify`, `llm`, `admission`.

**Response `200`** (rút gọn)

```json
{
  "id": "7b8f0d29-…", "status": "HIT", "partition": "95503c7831d2f7ed", "similarity": 0.8471, "entry_id": "…",
  "spans": [
    { "name": "identity", "title": "Danh tính & access signature", "start_ms": 0.0, "duration_ms": 0.4, "status": "ok",
      "data": { "user": "cskh1", "signature": "95503c7831d2f7ed", "collections": ["cskh", "internal_all", "public"], "signature_from_cache": true } },
    { "name": "cache_lookup", "title": "Tra cache (partition theo signature)", "duration_ms": 17.0, "status": "ok",
      "data": { "threshold": 0.75,
                "candidates": [ { "question": "Khách VIP được đổi trả trong bao lâu?", "similarity": 0.847,
                                  "passed": true, "reason": "thoả mọi điều kiện" } ] } }
  ],
  "audit": { "canaries": [ { "id": "vip_33", "collection": "cskh" }, { "id": "vip_47", "collection": "cskh" } ],
             "denied_collections": [], "checked_with_iam": true },
  "unauthorized": false
}
```

**Lỗi:** `404` nếu không có trace.

---

### `GET /api/console/cache/entries`

Thống kê cache, partition và danh sách entry (tối đa 200, theo thứ tự LRU).

**Response `200`** (rút gọn)

```json
{
  "stats": { "entries": 7 },
  "partitions": { "95503c7831d2f7ed": ["cskh1", "cskh2"], "1f0c…": ["khach"] },
  "entries": [
    { "entry_id": "89b29268-…", "partition": "95503c7831d2f7ed", "question": "Khách VIP được đổi trả trong bao lâu?",
      "answer": "…", "provenance": [ { "chunk_id": "…", "doc_id": "vip_return_exception", "version": 1, "collection": "cskh" } ],
      "intent": "return_policy", "entities": { "tier": "vip" }, "policy": "NORMAL", "ttl": 604800,
      "hits": 1, "ttl_left": 603712, "...": "..." }
  ]
}
```

---

### `DELETE /api/console/cache`

Xoá toàn bộ cache (vector trong Qdrant và các khoá `cache:*` trong Redis).

**Response `200`** `{ "deleted_keys": 23 }`

---

### `GET /api/console/security/events`

Sự kiện bảo mật, thống kê thời gian thu hồi quyền và các request bị audit đánh dấu vượt quyền.

**Response `200`** (rút gọn)

```json
{
  "events": [
    { "id": 22, "kind": "permission_change", "source": "keycloak",
      "occurred_at": "…", "detected_at": "…", "effective_at": "…",
      "summary": "<mô tả sự kiện Keycloak> -> tính lại signature: cskh1",
      "details": { "kind": "role_mapping", "usernames": ["cskh1"], "signatures_invalidated": 1 } }
  ],
  "revocation": { "n": 2, "avg_s": 1.24, "max_s": 1.35 },
  "unauthorized_traces": []
}
```

`kind` ∈ `permission_change`, `doc_update`. Thời gian thu hồi có hiệu lực = `effective_at − occurred_at`.

---

### `GET /api/console/stream?token=<access_token>`

Luồng Server-Sent Events. Token được truyền qua query string vì `EventSource` không gửi được header.

| Event | Data | Khi nào |
|---|---|---|
| `trace` | Tóm tắt trace (như một dòng của `/traces`) | Mỗi request xử lý xong |
| `audit` | `{ "id", "unauthorized", "audit" }` | Audit canary chạy xong |
| `security` | Một dòng `security_events` | Có thay đổi quyền hoặc tài liệu |
| `ping` | `{}` | Mỗi giây khi không có sự kiện, để giữ kết nối |

```text
event: trace
data: {"id": "7b8f0d29-…", "status": "HIT", "username": "cskh1", "latency_ms": 19.0, ...}
```

---

### `GET /api/console/admin/users`

Người dùng trong `acl.yaml` kèm vai trò, thuộc tính và các collection đọc được theo Keycloak tại thời điểm gọi.

**Response `200`** (rút gọn)

```json
{
  "users": [
    { "username": "sales_bac", "name": "Hùng Sales Bắc", "user_id": "…", "roles": ["employee", "sales"],
      "attributes": { "region": "north" },
      "collections_now": ["internal_all", "public", "sales_north"],
      "cached_signature": { "signature": "…", "collections": ["internal_all", "public", "sales_north"], "computed_at": 1794371838.2 } }
  ],
  "roles": ["customer", "employee", "cskh_agent", "hr", "sales", "ops_admin"],
  "collections": ["public", "internal_all", "cskh", "hr_confidential", "sales_north", "sales_south"]
}
```

---

### `POST /api/console/admin/users/{username}/roles`

Cấp hoặc thu hồi một vai trò, ghi thẳng vào Keycloak. Backend **không** tự xoá signature ở đây: Keycloak sinh admin event và `PermissionSync` xử lý, giống như khi quản trị viên đổi quyền trực tiếp trên Keycloak.

**Request body**

```json
{ "role": "cskh_agent", "grant": false }
```

**Response `200`**

```json
{ "ok": true, "username": "cskh1", "role": "cskh_agent", "grant": false }
```

**Lỗi:** `400` nếu vai trò không hợp lệ hoặc quản trị viên tự thu hồi `ops_admin`; `404` nếu không có người dùng.

---

### `GET /api/console/admin/documents`

Danh sách tài liệu, các phiên bản có sẵn và phiên bản đang dùng.

**Response `200`**

```json
[
  { "doc_id": "return_policy", "title": "Chính sách đổi trả hàng", "collection": "public",
    "versions": [1, 2], "current_version": 1, "updated_at": "2026-11-11T04:05:00+00:00" }
]
```

---

### `POST /api/console/admin/documents/{doc_id}/publish`

Xuất bản một phiên bản: nạp lại các đoạn tài liệu và xoá các cache entry có provenance chứa tài liệu này.

**Request body** `{ "version": 2 }`

**Response `200`**

```json
{
  "id": 23, "kind": "doc_update", "source": "admin_api",
  "occurred_at": "2026-11-11T04:37:58.351167+00:00",
  "summary": "return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry",
  "details": { "actor": "admin_ops", "doc_id": "return_policy", "from_version": 1, "to_version": 2, "chunks": 4,
               "invalidated_entries": ["89b29268-…", "13c22a20-…", "58268469-…", "09176751-…"] }
}
```

**Lỗi:** `404` nếu tài liệu hoặc phiên bản không tồn tại.

---

### `POST /api/console/admin/reset`

Khôi phục dữ liệu demo: vai trò về theo `acl.yaml`, tài liệu về phiên bản đầu, xoá cache và signature.

**Request body**

| Trường | Kiểu | Mô tả |
|---|---|---|
| `clear_history` | `boolean` | `true` thì xoá cả traces, security_events, sessions. Mặc định `false` |

**Response `200`** `{ "ok": true }`
