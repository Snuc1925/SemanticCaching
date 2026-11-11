# Đi theo một câu hỏi: luồng xử lý chi tiết của backend

Tài liệu này đi theo các yêu cầu **thật** qua từng hàm của backend: hàm nào gọi hàm nào, theo thứ tự nào, input/output là gì, và giải thích từng trường dữ liệu. Phần cuối gồm danh mục toàn bộ hàm/class và **các điểm có thể chưa hợp lý** để soát lại.

- Mọi giá trị (ID, điểm similarity, thời gian, token…) lấy từ **lần chạy thật ngày 11/11/2026**, ghi bằng bộ ghi lời gọi hàm `scripts/walkthrough/trace_calls.py` với các kịch bản trong `scripts/walkthrough/scenarios.py` (công cụ của skill `walkthrough`).
- Bản ghi đầy đủ từng lời gọi hàm (không lược bớt) nằm ở [walkthrough/raw/](walkthrough/raw/README.md). Tài liệu này là bản đã chọn lọc và giải thích.
- Ghi lại sau khi sửa code: `make trace` (cần `make infra-up` và đã `make setup`). ID và thời gian sẽ khác, nhưng cấu trúc giữ nguyên.
- Quên một khái niệm/tên biến (vd `resource_names`, `partition`, `provenance`)? Tra [DICTIONARY.md](DICTIONARY.md).
- Ký hiệu: `→` gọi hàm, `in:` tham số, `out:` giá trị trả về, `[x ms]` thời gian chạy. Đường dẫn hàm viết theo dạng `module.hàm` trong `backend/app/`.

## Mục lục
0. [Bản đồ module](#0-bản-đồ-module)
1. [IAM: Keycloak làm gì trong hệ thống](#1-iam-keycloak-làm-gì-trong-hệ-thống)
2. [Dữ liệu có sẵn trước khi hỏi (ingest)](#2-dữ-liệu-có-sẵn-trước-khi-hỏi-ingest)
3. [Khởi động backend](#3-khởi-động-backend)
4. [Luồng A: hỏi lần đầu → MISS](#4-luồng-a-hỏi-lần-đầu--miss) ← câu hỏi trong ảnh
5. [Luồng B: hỏi lại bằng câu khác → HIT](#5-luồng-b-hỏi-lại-bằng-câu-khác--hit)
6. [Luồng C: người ít quyền hơn hỏi cùng câu](#6-luồng-c-người-ít-quyền-hơn-hỏi-cùng-câu)
7. [Luồng D: câu hỏi cá nhân → NO_CACHE](#7-luồng-d-câu-hỏi-cá-nhân--no_cache)
8. [Luồng E: Console thu hồi quyền → đồng bộ → hỏi lại](#8-luồng-e-console-thu-hồi-quyền--đồng-bộ--hỏi-lại)
9. [Luồng F: Console xuất bản version tài liệu mới](#9-luồng-f-console-xuất-bản-version-tài-liệu-mới)
10. [Luồng G: Console đọc số liệu, stream, khôi phục demo](#10-luồng-g-console-đọc-số-liệu-stream-khôi-phục-demo)
11. [Các kiểu dữ liệu (dataclass) và ý nghĩa từng trường](#11-các-kiểu-dữ-liệu-dataclass-và-ý-nghĩa-từng-trường)
12. [Danh mục toàn bộ hàm/class](#12-danh-mục-toàn-bộ-hàmclass)
13. [Các điểm có thể chưa hợp lý](#13-các-điểm-có-thể-chưa-hợp-lý)

---

## 0. Bản đồ module

```
                      HTTP (token Keycloak)
                             │
                      main.py (FastAPI endpoints)
            ┌────────────────┼──────────────────────────────┐
            │                │                              │
         auth.py        pipeline.py  ──────────────┐      sync.py (thread nền + xuất bản tài liệu)
     (giải mã token)   (luồng 1 câu hỏi)           │        │
                             │                     │        │
   ┌──────────┬──────────┬───┴──────┬──────────┬───┴──────┐ │
access.py  embeddings  classifier  cache.py  retrieval  llm.py
(signature)   .py        .py      (cache)     .py     (Gemini)
   │                      │          │          │        │
   └──────── iam/keycloak.py ◄───────┘          │     prompts.py
             (gọi Keycloak)                     │
                                         documents.py ── chunking.py
tracing.py (trace/span → Postgres + Redis pub/sub)     audit.py (canary, chạy nền)
metrics.py (truy vấn số liệu cho Console)              db.py / clients.py / config.py (hạ tầng)
```

| Module | Vai trò một câu | Lưu/đọc ở đâu |
|---|---|---|
| `main` | Định nghĩa API; nhận request, gọi pipeline hoặc chức năng Console | – |
| `auth` | Giải mã token người dùng (JWT của Keycloak) thành `UserContext` | Keycloak (khoá công khai JWKS) |
| `pipeline` | Điều phối 8 bước xử lý một câu hỏi | – |
| `access` | Tính và cache **access signature** | Redis `sig:user:*` |
| `iam/keycloak` | Gọi Keycloak Admin API: đánh giá quyền, đổi role, đọc admin events | Keycloak |
| `embeddings` | Gọi OpenAI để lấy vector, có cache | Redis `emb:*` |
| `classifier` | Rule phân loại câu hỏi, intent, entity | `configs/classifier.yaml` |
| `cache` | Semantic cache: tra, lưu, xoá, LRU | Qdrant `semantic_cache` + Redis `cache:*` |
| `retrieval` | Tìm đoạn tài liệu có lọc theo collection | Qdrant `chunks` |
| `llm` / `prompts` | Gọi Gemini; prompt lấy từ YAML | `configs/prompts.yaml` |
| `documents` / `chunking` | Đọc Markdown, cắt chunk, nạp vào Qdrant, quản lý version | `data/pilot/docs`, Qdrant, Postgres `documents`, Redis `doc:version` |
| `sync` | Thread đọc admin events của Keycloak; xuất bản version tài liệu | Postgres `security_events` |
| `tracing` | Ghi trace từng request | Postgres `traces`, Redis pub/sub |
| `audit` | Kiểm tra rò rỉ bằng canary sau mỗi câu trả lời | Postgres `traces.audit` |
| `metrics` | SQL tổng hợp cho Console | Postgres |

---

## 1. IAM: Keycloak làm gì trong hệ thống

### 1.1 Keycloak giữ những gì
Keycloak là **nguồn quyết định quyền duy nhất**. Backend không tự lưu "ai được đọc gì"; mỗi lần cần là hỏi Keycloak. Mọi thứ dưới đây được `scripts/setup_keycloak.py` tạo từ `data/pilot/acl.yaml`.

| Khái niệm Keycloak | Trong hệ thống này | Giá trị thật |
|---|---|---|
| **Realm** | Một "không gian" người dùng/quyền riêng | `semcache` |
| **User** | Người dùng; có thể có **attribute** | `cskh1` (id `829671b9-…`), `sales_bac` có attribute `region=north` |
| **Realm role** | Vai trò gán cho user | `customer, employee, cskh_agent, hr, sales, ops_admin` |
| **Client `semcache-frontend`** | Ứng dụng web người dùng đăng nhập (public, PKCE) | Token người dùng có `azp = semcache-frontend` |
| **Client `semcache-backend`** | Backend; có **service account** và bật **Authorization Services** | uuid `b241a711-46be-488a-b226-d122149c1b86` |
| **Resource** (trên client backend) | Mỗi **collection** tài liệu là một resource | `collection:public`, `collection:cskh`, … (6 resource) |
| **Policy** | Một điều kiện | `p_cskh` (type role: có role `cskh_agent`), `p_region_north` (type regex: claim `region` khớp `^north$`) |
| **Permission** | Gắn resource với các policy, chiến lược UNANIMOUS = phải thoả tất cả | `read sales_north` = `p_sales` **và** `p_region_north` |

Cấu hình policy thật đọc từ Keycloak:
```
role   p_any_user     roles=[customer, employee] (required=false → có 1 trong 2 là đủ), fetchRoles=true
role   p_employee     roles=[employee]
role   p_cskh         roles=[cskh_agent]
role   p_hr           roles=[hr]
role   p_sales        roles=[sales]
regex  p_region_north targetClaim=region, pattern=^north$
regex  p_region_south targetClaim=region, pattern=^south$
resource-permission  read public | read internal_all | read cskh | read hr_confidential | read sales_north | read sales_south   (UNANIMOUS)
```
`fetchRoles=true` nghĩa là Keycloak đọc role **hiện tại trong cơ sở dữ liệu** của user, không dựa vào role ghi trong token. Nhờ vậy thu hồi role có hiệu lực ngay khi đánh giá.

### 1.2 Hai loại token
**(a) Token người dùng.** Trình duyệt đăng nhập qua `semcache-frontend` rồi gửi token lên backend ở header `Authorization: Bearer …`. Nội dung thật đã giải mã (user `sales_bac`):
```json
{"iss": "http://localhost:8080/realms/semcache", "sub": "eea2aee0-a6a6-4a31-9243-6534436b6068",
 "azp": "semcache-frontend", "preferred_username": "sales_bac", "name": "Hùng Sales Bắc",
 "realm_access": {"roles": ["default-roles-semcache","offline_access","uma_authorization","employee","sales"]},
 "exp": 1794371013, "iat": 1794370113}
```
- `sub` dùng làm `user_id` ở mọi nơi trong backend.
- Token **không có** claim `region`. Mapper `region` chỉ gắn vào client backend (mục 1.3).
- Token sống 15 phút (`exp - iat = 900`). Role trong token có thể cũ tới 15 phút. Backend **không** dùng role trong token để quyết định đọc tài liệu, nhưng **có** dùng để kiểm tra quyền vào Console (xem mục 13, điểm 9).

**(b) Token service account của backend.** `KeycloakAdmin.token()` xin token này bằng `client_credentials` (client id + secret), cache lại đến 30 giây trước khi hết hạn. Đây là token để gọi Admin API:
```json
{"azp": "semcache-backend", "preferred_username": "service-account-semcache-backend",
 "resource_access": {"realm-management": {"roles": ["view-realm","view-events","manage-users","view-users",
   "view-clients","manage-authorization","view-authorization","manage-clients","query-clients","query-groups","query-users"]}, …}}
```
Các role `realm-management` này cho phép: đọc user, đổi role (`manage-users`), đánh giá policy (`manage-authorization`), đọc admin events (`view-events`).

### 1.3 Đánh giá quyền: API `policy/evaluate`
Đây là lời gọi IAM quan trọng nhất, nằm trong `KeycloakAdmin.evaluate(user_id, resource_names)`:
```
POST /admin/realms/semcache/clients/b241a711-…/authz/resource-server/policy/evaluate
{"userId": "<id user cần hỏi>", "clientId": "b241a711-…", "resources": [{"_id": "...", "name": "collection:sales_north"}],
 "roleIds": [], "entitlements": false, "context": {"attributes": {}}}
```
- `resources: []` thì Keycloak đánh giá **mọi** resource. Cách này dùng khi tính signature.
- Keycloak tự dựng danh tính của user **từ dữ liệu hiện tại** (role, attribute qua mapper của client backend, nên có claim `region`), rồi chạy policy.

Response thật, ví dụ ABAC (cùng có role `sales`, khác `region`):
```
sales_bac → collection:sales_north: PERMIT   (read sales_north: p_sales=PERMIT, p_region_north=PERMIT)
sales_nam → collection:sales_north: DENY     (read sales_north: p_sales=PERMIT, p_region_north=DENY)
```
`evaluate` chuyển kết quả thành `{tên resource: True/False}`. Trong backend có **4 nơi** gọi đánh giá quyền:

| Nơi gọi | Mục đích | Resource hỏi |
|---|---|---|
| `access.refresh` → `list_accessible_collections` | Tính signature | tất cả |
| `pipeline.answer` bước iam_verify → `check_collections` | Kiểm tra lại các đoạn vừa truy xuất (post-verify) | collection của các chunk |
| `cache.lookup` → `reverify` → `check_collections` | Điều kiện 6 khi HIT | collection trong provenance của entry |
| `audit.run` → `check_collections` | Audit canary | collection của canary tìm thấy |

Nếu gọi Keycloak lỗi, `check_collections` trả `False` cho mọi collection (fail-closed).

### 1.4 Admin events: cách backend biết quyền đã đổi
Realm bật `adminEventsEnabled`, nên mỗi thay đổi qua Admin API (kể cả thao tác trong giao diện admin của Keycloak) đều sinh một event. Event thật khi cấp lại role:
```json
{"time": 1794370061899, "operationType": "CREATE", "resourceType": "REALM_ROLE_MAPPING",
 "resourcePath": "users/829671b9-5f8b-431d-9b2f-8a31158a3a2d/role-mappings/realm",
 "representation": "[{\"id\":\"fce33e7e-…\",\"name\":\"cskh_agent\",\"composite\":false}]",
 "authDetails": {"clientId": "b241a711-…", "userId": "4e121ac4-…", "ipAddress": "172.30.0.1"}}
```
- Event **không có trường `id`** (Keycloak 26.0). Vì vậy `_event_key` ghép `time|operationType|resourceType|resourcePath|hash(representation)` làm khoá chống trùng.
- `resourcePath` bắt đầu bằng `users/<id>` cho biết user nào bị ảnh hưởng.
- `KeycloakEventSource.poll` phân loại:
  - `REALM_ROLE_MAPPING`, `CLIENT_ROLE_MAPPING`, `GROUP_MEMBERSHIP`, `USER` → ảnh hưởng **một user**.
  - `AUTHORIZATION_POLICY`, `AUTHORIZATION_RESOURCE`, `REALM_ROLE`, … → ảnh hưởng **mọi user** (`affects_all`).

Luồng đầy đủ ở [mục 8](#8-luồng-e-console-thu-hồi-quyền--đồng-bộ--hỏi-lại).

---

## 2. Dữ liệu có sẵn trước khi hỏi (ingest)
`make seed` → `scripts/seed.py` → `documents.ingest_all_initial()` → `documents.ingest(doc_id, 1)` cho từng tài liệu. Hàm `ingest` cũng được dùng lại khi xuất bản version mới. Bản ghi thật của `ingest` nằm ở [mục 9](#9-luồng-f-console-xuất-bản-version-tài-liệu-mới); dưới đây là tóm tắt.

```
→ documents.ingest(doc_id='return_policy', version=1)
  → documents.parse_file(path=data/pilot/docs/return_policy.v1.md)
      out: ({doc_id, title:'Chính sách đổi trả hàng', collection:'public', version:1}, '<nội dung markdown>')
  → chunking.chunk_document(doc_id, version, collection, title, md, max_tokens=400, min_tokens=80, overlap=50)
      → _sections(md, title): tách theo tiêu đề '##' → 6 mục
      gộp mục ngắn: 'Phạm vi áp dụng' (60 token < 80) + 'Thời hạn đổi trả' → 136 token
                    'Hàng điện tử…' (61 token) + 'Hoàn tiền' → 121 token
      out: [Chunk ×4]  (chunk_id = sha1(doc_id|version|section_path|index)[:16])
  → embeddings.embed([chunk.embed_text ×4])          # embed_text = "[Tiêu đề > Mục]\n" + nội dung
      out: ([vector 1536 số ×4], 487 token, False)
  → Qdrant 'chunks': xoá mọi point có doc_id='return_policy', upsert 4 point mới
  → Postgres documents: upsert (doc_id, title, collection, version)
  → Redis HSET doc:version return_policy 1
  out: 4   (số chunk)
```

Một point trong Qdrant collection `chunks` (xem bằng `scripts/show_chunks.py`):
```
id      = uuid5(chunk_id)            vector = 1536 số (đã chuẩn hoá L2)
payload = {chunk_id:'232c157bca68b49d', doc_id:'return_policy', version:1, collection:'public',
           title:'Chính sách đổi trả hàng', section_path:'Chính sách đổi trả hàng > Phạm vi áp dụng',
           text:'Chính sách áp dụng cho mọi đơn hàng … **Thời hạn đổi trả** Khách hàng được đổi trả … **7 ngày** …'}
```
Payload `collection` được đánh chỉ mục (payload index) để lọc nhanh khi truy xuất.

---

## 3. Khởi động backend
`uvicorn app.main:app` → `main.lifespan` [235 ms] (bản ghi: [00_startup](walkthrough/raw/00_startup.md)):
```
→ db.init_schema()                       CREATE TABLE IF NOT EXISTS documents, sessions, messages, traces, security_events
→ prompts.validate({'rag_answer': {question, context, history, no_answer}})
      kiểm tra prompt chỉ dùng các biến code truyền vào → sai thì dừng khởi động
→ documents.ensure_collection()          tạo Qdrant 'chunks' nếu chưa có (cần dim → gọi embeddings.dim())
→ cache.ensure_collection()              tạo Qdrant 'semantic_cache' nếu chưa có
→ sync.PermissionSync.__init__()         KeycloakAdmin() + KeycloakEventSource(since_ms = thời điểm hiện tại)
→ sync.PermissionSync.start()            chạy thread 'permission-sync': cứ 2 s gọi poll_once()
```
Event xảy ra **trước** khi backend khởi động bị bỏ qua (`since_ms` = lúc khởi động). Điều này đúng ý đồ, vì signature cũ trong Redis vẫn có TTL chặn trên.

---

## 4. Luồng A: hỏi lần đầu → MISS
**Kịch bản:** `cskh1` (role `employee, cskh_agent`) mở session mới và hỏi *"Khách VIP được đổi trả trong bao lâu?"*. Trước đó `cskh1` đã gọi `GET /api/me`, nên signature đã có trong Redis.
Bản ghi đầy đủ: [02_chat_miss](walkthrough/raw/02_chat_miss.md). Tổng thời gian **5322 ms**.

### 4.0 (trước đó) GET /api/me tính signature lần đầu
Bản ghi: [01_me](walkthrough/raw/01_me.md).
```
→ main.me(user)
  → access.get(user)                                 Redis GET sig:user:829671b9-… → không có
    → access.refresh(user)
      → KeycloakAccessControl.list_accessible_collections(user)
        → KeycloakAdmin.evaluate(user_id, resource_names=None)
          → client_uuid()   GET /clients?clientId=semcache-backend → 'b241a711-…'  (cache trong object)
          → request('POST', '/clients/b241a711-…/authz/resource-server/policy/evaluate', json={userId…, resources: []})
          out: {collection:cskh: True, collection:sales_north: False, collection:hr_confidential: False,
                collection:internal_all: True, collection:public: True, collection:sales_south: False}
        out: {'public', 'internal_all', 'cskh'}            (bỏ tiền tố 'collection:', chỉ giữ True)
      → access.compute_hash(['keycloak:cskh','keycloak:internal_all','keycloak:public'])
            = sha256("v1|keycloak:cskh,keycloak:internal_all,keycloak:public")[:16]
        out: '95503c7831d2f7ed'
      Redis SET sig:user:829671b9-… {signature, collections, computed_at, username}  EX 300
      Redis HSET sig:known 829671b9-… {username:'cskh1', signature:'95503c7831d2f7ed'}
      out: Signature(signature='95503c7831d2f7ed', collections=['cskh','internal_all','public'], from_cache=False)
  out: {user_id, username:'cskh1', roles:[…], is_console: False, signature:'95503c7831d2f7ed', collections:[…]}
```

### 4.1 Xác thực
```
→ auth.current_user(request)                          FastAPI gọi trước endpoint (Depends)
  → auth.decode(token='eyJhbGciOiJSUzI1NiIs…')
      lấy khoá công khai từ JWKS của Keycloak (PyJWKClient, có cache)
      kiểm tra chữ ký RS256 + iss == 'http://localhost:8080/realms/semcache' + azp == 'semcache-frontend'
    out: UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1',
                     roles=('default-roles-semcache','offline_access','uma_authorization','employee','cskh_agent'),
                     display_name='Lan CSKH')
```

### 4.2 `main.chat`: quản lý session, rồi gọi pipeline
```
→ main.chat(body=ChatIn{message:'Khách VIP được đổi trả trong bao lâu?', session_id:None}, bg, user)
  session_id rỗng → tạo mới:
  → db.execute("INSERT INTO sessions(id,user_id,username,title) …", ('7808365c-…', '829671b9-…', 'cskh1', 'Khách VIP được đổi trả trong bao lâu?'))
  → db.fetch_all("SELECT role, content FROM messages WHERE session_id=%s ORDER BY created_at DESC LIMIT 4")  out: []   (history)
  → db.execute("INSERT INTO messages(... 'user', câu hỏi)")
  → tracing.Trace.__init__(user_id, username, question, session_id)     tạo trace id '69867628-…', status mặc định 'ERROR'
  → pipeline.answer(user, question, session_id, history=[], tr)          ← mục 4.3
  → tracing.Trace.save()                                                   ← mục 4.4 (luôn chạy, kể cả khi lỗi)
  → db.execute("INSERT INTO messages(... 'assistant', answer, trace_id, cache_status='MISS', citations)")
  → db.execute("UPDATE sessions SET updated_at=now()")
  bg.add_task(audit.run, trace_id, user, answer)                           ← mục 4.5, chạy SAU khi đã trả response
  out (JSON trả về frontend): {session_id:'7808365c-…', message_id, trace_id:'69867628-…', status:'MISS',
       answer:'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày … [c2]. Trưởng ca CSKH … 47 ngày [c2].',
       citations:[{label:'c2', doc_id:'vip_return_exception', title, section, collection:'cskh', version:1}],
       latency_ms:5284.3, similarity:None, policy:'NORMAL'}
```
`history` lấy 4 tin nhắn gần nhất, đảo lại theo thứ tự thời gian. Nó **chỉ được đưa vào prompt khi câu hỏi là BYPASS** (câu nối tiếp), xem bước 7.

### 4.3 `pipeline.answer`: 8 bước
Mỗi bước nằm trong `with tr.span(name, title) as d:`. Dict `d` là phần `data` của span, hiển thị trên Console.

**Bước 1: identity** [`access.get` 1.5 ms]
```
→ access.get(user)       Redis có sẵn từ /api/me
  out: Signature(signature='95503c7831d2f7ed', collections=['cskh','internal_all','public'], from_cache=True)
tr.set(partition='95503c7831d2f7ed')
```

**Bước 2: embed** [832 ms]
```
→ embeddings.embed_one('Khách VIP được đổi trả trong bao lâu?')
  → embeddings.embed([text])
      Redis MGET emb:text-embedding-3-small:<sha1(text)> → không có
      OpenAI embeddings.create → 1 vector, chuẩn hoá L2, Redis SET … EX 30 ngày
    out: ([<vector 1536: -0.0111, 0.0120, …>], 15 token, False)
  out: (vector, 15, False)        # (vector, số token tính phí, lấy hết từ cache?)
```

**Bước 3: classify** [550 ms, chủ yếu do khởi động lạnh, xem mục 13 điểm 3]
```
→ classifier.classify(question, vec)
  → cache_policy(question)
      normalize → 'khách vip được đổi trả trong bao lâu?'
      _has(text, NO_CACHE.keywords ['của tôi', …])           → None
      kiểm tra BYPASS.starts_with ['thế còn', 'còn ', …]     → không khớp
      _has(text, BYPASS.keywords ['cái đó', …])               → None
      số từ = 8 ≥ min_words 4
      _has(text, SHORT_TTL.keywords ['hôm nay', …])           → None
    out: ('NORMAL', 'câu hỏi tĩnh')
  → intent(vec)
    → _intent_centroids()   LẦN ĐẦU trong tiến trình: embed 16 câu mẫu (236 token) → trung bình mỗi intent → cache (lru_cache)
    tích vô hướng vec · centroid của 8 intent → lớn nhất: return_policy = 0.72  (≥ min_similarity 0.45)
    out: ('return_policy', 0.72)
  → extract_entities(question)       tìm cụm từ trong từ điển entities (regex có ranh giới từ)
    out: {'tier': 'vip'}
  out: Classification(policy='NORMAL', reason='câu hỏi tĩnh', intent='return_policy', intent_similarity=0.72, entities={'tier':'vip'})
cacheable = cache.enabled AND policy ∈ {NORMAL, SHORT_TTL} → True
→ prompts.version('rag_answer')  = 'v' + version + '-' + sha256(json prompt)[:8]   out: 'v1-8cc4d02d'
```

**Bước 4: cache_lookup** [24 ms]
```
→ cache.lookup(vec, partition='95503c7831d2f7ed', intent='return_policy', entities={'tier':'vip'},
               prompt_version='v1-8cc4d02d', reverify=<hàm gọi check_collections>)
  → threshold_for('return_policy')  out: 0.75
  Qdrant query 'semantic_cache' với filter partition='95503c7831d2f7ed', limit 3 → [] (partition chưa có entry)
  out: LookupResult(hit=None, similarity=None, candidates=[])
```

**Bước 5: retrieval** [20.8 ms]
```
→ retrieval.search(vec, collections=['cskh','internal_all','public'])
  Qdrant query 'chunks', filter collection ∈ [...] (LỌC TRƯỚC theo quyền), limit top_k=5, bỏ score < 0.25
  out (5 Retrieved, xếp theo score):
   c1 0.7714 vip_return_exception  cskh   '… > Khách hạng Bạc'                  "Khách hạng Bạc được đổi trả trong vòng 10 ngày … **Lưu ý bảo mật** Không thông báo các thời hạn ngoại lệ…"
   c2 0.7577 vip_return_exception  cskh   '… > Thời hạn đổi trả của khách VIP'   "Khách hàng hạng VIP được đổi trả trong vòng **33 ngày** …"
   c3 0.5546 membership_faq        public '… > Quyền lợi chung'
   c4 0.5449 return_policy         public '… > Phạm vi áp dụng'                  (chứa cả "Thời hạn đổi trả … 7 ngày")
   c5 0.5334 complaint_handling    cskh   '… > Thời gian phản hồi'
```

**Bước 6: iam_verify** [36.3 ms]
```
→ KeycloakAccessControl.check_collections(user, {'cskh','public'})      # tập collection của 5 chunk
  → KeycloakAdmin.evaluate(user_id, ['collection:cskh','collection:public'])
    → resources()   LẦN ĐẦU: GET …/resource-server/resource → {tên: _id} cho 6 resource (cache 60 s)
    → request('POST', '…/policy/evaluate', json={userId, clientId, resources:[{_id,name}×2], …})
    out: {collection:cskh: True, collection:public: True}
  out: {'cskh': True, 'public': True}
allowed = 5 chunk, blocked = []        (nếu có chunk bị chặn → loại khỏi context + xoá signature)
```

**Bước 7: llm** [3772 ms, trong đó Gemini 3056 ms]
```
→ retrieval.format_context(allowed)     gán nhãn c1..c5, mỗi đoạn: "[c1] (Nguồn: <section_path>)\n<text>"
→ llm.generate('rag_answer', question=…, context='[c1] (Nguồn: …) …(1.7k ký tự)', history='(không có)',
               no_answer='Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.')
  → prompts.render('rag_answer', **variables)
      → variables('rag_answer') = {'question','context','history','no_answer'}; thiếu biến → PromptError
      out: (system prompt, user prompt)
  → Gemini generate_content(model='gemini-3.5-flash-lite', system_instruction, temperature 0.1, max_output_tokens 600)
    (lỗi thì thử lại tối đa 3 lần, chờ 1.5 s, 3 s)
  out: LLMResult(text='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến tối đa 47 ngày [c2].',
                 tokens_in=725, tokens_out=44, latency_ms=3056, model='gemini-3.5-flash-lite', prompt_version='v1-8cc4d02d')
→ pipeline._citations(answer, allowed)   tìm [cN] trong câu trả lời → map sang chunk
  out: [{label:'c2', doc_id:'vip_return_exception', title, section:'… > Thời hạn đổi trả của khách VIP', collection:'cskh', version:1}]
→ llm.cost_usd(725, 44, embed_tokens=15) = (725×0.10 + 44×0.40 + 15×0.02)/1e6 ≈ $0.0001
```

**Bước 8: admission** [cache.store 46.8 ms]
```
Kiểm tra (đều đạt): cacheable ✓; có context ✓; câu trả lời không chứa câu "không tìm thấy" ✓; có ≥1 trích dẫn hợp lệ ✓
→ cache.new_entry_id()  out: '13c22a20-a6b2-4a03-9448-46772e13273d'
→ cache.store(CacheEntry(
      entry_id='13c22a20-…', partition='95503c7831d2f7ed', question='Khách VIP được đổi trả trong bao lâu?',
      answer='…33 ngày… [c2] …47 ngày [c2].', citations=[c2],
      provenance=[5 Provenance: vip_return_exception v1 ×2, membership_faq v1, return_policy v1, complaint_handling v1],   ← cả 5 chunk trong context
      intent='return_policy', entities={'tier':'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d',
      model='gemini-3.5-flash-lite', created_at=<epoch>, ttl=604800 (7 ngày),
      gen_tokens_in=725, gen_tokens_out=44, gen_cost_usd=0.0001, gen_latency_ms=3056, hits=0, last_hit=None), vec)
  → ensure_collection()
  Qdrant upsert 'semantic_cache': id=entry_id, vector=vec (câu HỎI), payload={entry_id, partition}
  Redis (1 pipeline):
     SET  cache:entry:13c22a20-…  <JSON entry>  EX 604800
     SADD cache:doc:vip_return_exception / membership_faq / return_policy / complaint_handling  13c22a20-…   (reverse index)
     ZADD cache:lru  13c22a20-… <created_at>
  → evict_if_needed()   số entry ≤ max_entries 5000 → []
tr.set(status='MISS', latency_ms=5284.3, llm_tokens_in=725, llm_tokens_out=44, cost_usd=…)
out: (ChatResult(trace_id='69867628-…', status='MISS', answer, citations, latency_ms=5284.3, policy='NORMAL', similarity=None), tr)
```

### 4.4 Lưu trace và phát realtime
```
→ tracing.Trace.save()
  → db.execute("INSERT INTO traces(... 20 cột ..., spans)")     spans = list 8 span {name,title,start_ms,duration_ms,status,data}
  → tracing.summary(trace_id)  → SELECT các cột tóm tắt  → jsonable (đổi datetime/UUID sang chuỗi)
  → tracing.publish('trace', summary)   Redis PUBLISH semcache:events {"type":"trace","data":{…}}
                                        → Console (SSE) nhận và chèn dòng mới vào bảng Request
```

### 4.5 Audit canary (chạy nền, sau khi đã trả response) [45.1 ms]
```
→ audit.run(trace_id, user, answer)
  → audit.find(answer)
    → audit.canaries()   LẦN ĐẦU: đọc data/pilot/canaries.yaml, compile regex (lru_cache)
    out: [{id:'vip_33', collection:'cskh'}, {id:'vip_47', collection:'cskh'}]
  → KeycloakAccessControl.check_collections(user, {'cskh'})     # hỏi IAM TẠI THỜI ĐIỂM AUDIT
    out: {'cskh': True}      → cskh1 có quyền → không vi phạm
  → db.execute("UPDATE traces SET audit=…, unauthorized=False")
  → tracing.publish('audit', {id, unauthorized: False, audit})
  out: {canaries:[vip_33, vip_47], denied_collections: [], checked_with_iam: True}
```

---

## 5. Luồng B: hỏi lại bằng câu khác → HIT
**Kịch bản:** `cskh1` hỏi tiếp **trong cùng session**: *"Thời hạn đổi trả hàng cho khách VIP là bao lâu?"*. Bản ghi: [03_chat_hit](walkthrough/raw/03_chat_hit.md). Tổng **915 ms** (so với 5322 ms khi MISS; phần lớn là gọi OpenAI để embed câu hỏi mới, xem mục 13 điểm 4).

Khác với luồng A:
```
→ main.chat(body={message, session_id:'7808365c-…'})
  → main._own_session(session_id, user)   SELECT sessions WHERE id → user_id phải trùng, không thì 404
  history = [{user:'Khách VIP…'}, {assistant:'Khách hàng hạng VIP …'}]     (có nhưng bước 7 không dùng vì policy NORMAL)
  → pipeline.answer(...)
    1 identity   access.get → Signature('95503c7831d2f7ed', from_cache=True)                         2 ms
    2 embed      câu mới chưa có cache → gọi OpenAI → 21 token                                         844 ms
    3 classify   ('NORMAL', intent 'return_policy' 0.6918, entities {'tier':'vip'})  (centroid đã cache) 0.7 ms
    4 cache_lookup                                                                                       39 ms
```
**Chi tiết `cache.lookup`: 6 điều kiện, giá trị thật**
```
Qdrant query 'semantic_cache' filter partition='95503c7831d2f7ed' → 1 điểm: entry 13c22a20-…, score 0.8471
→ cache.get_entry('13c22a20-…')   Redis GET cache:entry:… → CacheEntry.from_json
  (1) cùng partition                      → đã lọc trong Qdrant
  (2) similarity 0.8471 ≥ ngưỡng 0.75     ✓
  (3) entities {'tier':'vip'} == {'tier':'vip'}   ✓
  (4a) prompt_version 'v1-8cc4d02d' == 'v1-8cc4d02d'   ✓
  (4b) → cache._stale_docs(e)
         → documents.current_versions(['complaint_handling','membership_faq','return_policy','vip_return_exception'])
             Redis HMGET doc:version … → {…: 1, …: 1, …: 1, …: 1}
         so với version trong provenance → không tài liệu nào đổi → []   ✓
  (5) now - created_at < ttl 604800        ✓
  (6) reverify({'public','cskh'}) → check_collections → evaluate → {public: True, cskh: True}   ✓  (17 ms)
  → candidate.passed = True, reason 'thoả mọi điều kiện'
  → cache._touch(e): hits 0→1, last_hit = now; Redis SET cache:entry (giữ TTL còn lại), ZADD cache:lru (cập nhật LRU)
out: LookupResult(hit=CacheEntry(13c22a20-…), similarity=0.8471, candidates=[Candidate(…, passed=True)])
```
Sau đó vào nhánh HIT, **bỏ qua bước 5 đến 8**:
```
span cache_hit: {entry_id, cached_question:'Khách VIP được đổi trả trong bao lâu?', hits:1, provenance, saved_tokens: 769, saved_cost_usd}
tr.set(status='HIT', similarity=0.8471, cost_usd=llm.cost_usd(0,0,21), saved_tokens=725+44, saved_cost_usd=…)
out: ChatResult(status='HIT', answer=<answer của entry>, citations=<citations của entry>, latency_ms=885.9)
```
Audit vẫn chạy như mục 4.5 (câu trả lời từ cache cũng được kiểm tra).

Nếu một điều kiện trượt, `Candidate.reason` ghi lý do. Đây chính là cột "Kết luận" trên Console:

| Điều kiện trượt | `reason` |
|---|---|
| (2) | `similarity 0.713 < ngưỡng 0.75` |
| (3) | `entity khác: câu hỏi {'package': 'vang'} vs entry {'package': 'bac'}` |
| (4a) | `prompt đã đổi (v1-xxxx -> v1-yyyy)` |
| (4b) | `tài liệu đã đổi version: return_policy v1->v2` |
| (5) | `hết TTL` |
| (6) | `IAM re-verify từ chối collection: cskh` (đồng thời xoá signature của user) |
| entry đã hết TTL trong Redis nhưng vector còn | `entry đã hết hạn (TTL)` (đồng thời xoá vector mồ côi) |

---

## 6. Luồng C: người ít quyền hơn hỏi cùng câu
**Kịch bản:** `khach` (chỉ role `customer`) hỏi *"Khách VIP được đổi trả trong bao lâu?"*. Bản ghi: [04_other_partition](walkthrough/raw/04_other_partition.md).
```
1 identity  access.get → không có trong Redis → access.refresh → evaluate(tất cả) → {'public'}
            → compute_hash(['keycloak:public']) = '3963a48f4b463545'   (KHÁC partition của cskh1)
3 classify  giống hệt cskh1: NORMAL, return_policy, {'tier':'vip'}
4 lookup    Qdrant filter partition='3963a48f4b463545' → [] → MISS
            → entry 13c22a20 của cskh1 (chứa "33 ngày") KHÔNG BAO GIỜ được xét, dù câu hỏi giống hệt
5 retrieval filter collection ∈ ['public'] → chỉ thấy membership_faq, return_policy, …  (không thấy tài liệu cskh)
6 iam_verify {'public': True}
7 llm       'Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c2].'  (605 → 22 token, 1959 ms)
8 admission lưu entry mới vào partition '3963a48f4b463545'
audit       find() → [] (không có canary) → không cần gọi IAM
```
Chặn rò rỉ diễn ra ở **hai lớp độc lập**: (1) partition khác nên không thấy entry của cskh1; (2) retrieval chỉ tìm trong collection được phép.

---

## 7. Luồng D: câu hỏi cá nhân → NO_CACHE
**Kịch bản:** `khach` hỏi *"Đơn hàng của tôi đang ở đâu rồi?"*. Bản ghi: [05_no_cache](walkthrough/raw/05_no_cache.md).
```
3 classify  cache_policy: _has(text, NO_CACHE.keywords) → 'của tôi'
            out: Classification(policy='NO_CACHE', reason="câu hỏi cá nhân (từ khoá 'của tôi')", intent='shipping' 0.5874, entities={})
            cacheable = False → BỎ QUA bước 4 (không tra cache)
5 retrieval vẫn chạy (public) → shipping_policy …
7 llm       'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'
8 admission admitted=False, reasons=["chính sách NO_CACHE: câu hỏi cá nhân (từ khoá 'của tôi')",
                                     "câu trả lời 'không tìm thấy' (không cache …)"]
status trả về = 'NO_CACHE'   (BYPASS tương tự; khác ở chỗ bước 7 đưa history vào prompt)
```

---

## 8. Luồng E: Console thu hồi quyền → đồng bộ → hỏi lại
### 8.1 Console gọi backend, backend ghi vào Keycloak
Bản ghi: [06_revoke](walkthrough/raw/06_revoke.md).
```
POST /api/console/admin/users/cskh1/roles  {role:'cskh_agent', grant:false}   (token của admin_ops)
→ auth.current_user → decode → UserContext(admin_ops, roles=(…, 'ops_admin', 'employee'))
→ auth.console_user(user)     'ops_admin' ∈ user.roles ✓ (nếu không → 403)
→ main.admin_set_role(username='cskh1', body=RoleIn{role:'cskh_agent', grant:False}, actor=admin_ops)
  → main._acl()                đọc data/pilot/acl.yaml → kiểm tra role hợp lệ; chặn tự thu hồi ops_admin của chính mình
  → KeycloakAdmin.find_user('cskh1')            GET /users?username=cskh1&exact=true → {id:'829671b9-…', …}
  → KeycloakAdmin.set_realm_role(user_id, 'cskh_agent', grant=False)
    → realm_role('cskh_agent')                   GET /roles/cskh_agent → {id:'fce33e7e-…', name:'cskh_agent'}
    → request('DELETE', '/users/829671b9-…/role-mappings/realm', json=[{id, name}])   → HTTP 204
  out: {ok: True, username:'cskh1', role:'cskh_agent', grant: False}
```
Endpoint **không tự xoá signature**. Đây là chủ ý thiết kế: hệ thống phải phát hiện thay đổi giống như khi quản trị viên đổi quyền trực tiếp trong Keycloak.

### 8.2 Keycloak sinh admin event, thread nền phát hiện
```
[thread permission-sync, 0,13 s sau]
→ sync.PermissionSync.poll_once()
  → KeycloakEventSource.poll()
    → KeycloakAdmin.admin_events(max_results=200)     GET /admin-events?max=200
    lọc event có time ≥ last_ms và _event_key chưa thấy:
    → _event_key(e) = '1794371861745|DELETE|REALM_ROLE_MAPPING|users/829671b9-…/role-mappings/realm|35052e3dac'
    resourceType REALM_ROLE_MAPPING + path users/<id> → ảnh hưởng 1 user
    out: [AccessChangeEvent(occurred_at=04:37:41.745, kind='role_mapping',
                            summary='DELETE REALM_ROLE_MAPPING (users/829671b9-…/role-mappings/realm)',
                            user_ids=['829671b9-…'], affects_all=False, raw={…})]
  với mỗi event:
  detected = now (04:37:41.870)
  → access.invalidate('829671b9-…')        Redis DEL sig:user:829671b9-… → True
  → request('GET', '/users/829671b9-…')     lấy username để ghi log → 'cskh1'
  → sync.record_event(kind='permission_change', source='keycloak',
        occurred_at=04:37:41.745, detected_at=04:37:41.870, effective_at=04:37:41.899,
        summary='DELETE REALM_ROLE_MAPPING (…) -> tính lại signature: cskh1',
        details={kind:'role_mapping', user_ids, usernames:['cskh1'], signatures_invalidated:1, operation:'DELETE',
                 representation:'[{"id":"fce33e7e-…","name":"cskh_agent",…}]'})
    → db INSERT security_events … RETURNING *  → id 22
    → tracing.publish('security', …)     → trang Bảo mật trên Console cập nhật
  out: 1   (số event đã xử lý)
```
**Revocation window = effective_at − occurred_at = 0,15 s** ở lần chạy này (lần chạy trước: 1,60 s). Thời gian này chủ yếu là chờ tới lượt poll kế tiếp, nên dao động từ gần 0 đến khoảng 2 s (chu kỳ poll) tuỳ thời điểm thu hồi.

### 8.3 cskh1 hỏi lại
Bản ghi: [07_after_revoke](walkthrough/raw/07_after_revoke.md).
```
1 identity  access.get → Redis không còn sig:user:829671b9-… → access.refresh
            → evaluate(tất cả) → {collection:cskh: False, internal_all: True, public: True, …}
            → compute_hash(['keycloak:internal_all','keycloak:public']) = '1fb84ec24c927b56'   ← PARTITION MỚI
4 lookup    filter partition='1fb84ec24c927b56' → [] → MISS   (entry 13c22a20 ở partition cũ không bị chạm tới)
5 retrieval filter collection ∈ ['internal_all','public'] → không còn tài liệu cskh
6 iam_verify {'public': True}
7 llm       trả lời theo chính sách công khai (7 ngày), không có 33/47 ngày
```
Entry `13c22a20` **không bị xoá**: `cskh2` (vẫn còn role) vẫn dùng đúng entry đó. Đây là cách giải quyết "partial information leakage" theo thiết kế (plan mục 4.4).

**Nếu poller chậm hoặc lỗi:** signature cũ còn trong Redis tối đa 300 s. Trong khoảng đó, nếu cskh1 hỏi câu trúng entry cũ, điều kiện (6) `reverify` hỏi Keycloak và nhận `cskh: False`. Khi đó request bị MISS và signature bị xoá. Đã quan sát được thật ở lần chạy ngày 10/11 (xem STATUS.md mục 4).

---

## 9. Luồng F: Console xuất bản version tài liệu mới
Bản ghi: [08_publish](walkthrough/raw/08_publish.md). Trước đó `khach` đã hỏi về đổi trả, tạo thêm entry dùng `return_policy`.
```
POST /api/console/admin/documents/return_policy/publish {version: 2}
→ auth.console_user ✓
→ main.admin_publish(doc_id='return_policy', body={version:2}, actor)
  → documents.available_versions()       đọc front matter của mọi file *.v*.md
    out: {…, return_policy: {title, collection:'public', versions:[1, 2]}, …}    → version 2 tồn tại ✓
  → sync.publish_document_version('return_policy', 2, 'admin_ops')                       [957 ms]
    → documents.current_version('return_policy')  Redis HGET doc:version → 1
    → documents.ingest('return_policy', 2)                                               [904 ms]
      → parse_file(return_policy.v2.md)
      → chunking.chunk_document(…, version=2)                                          [490 ms, xem mục 13 điểm 3]
          _sections → 6 mục; ntokens từng mục: Phạm vi 60, Thời hạn …, Điều kiện 91, Hàng điện tử 61, Hoàn tiền …, Không áp dụng …
          gộp: 'Phạm vi'(60<80) + 'Thời hạn' → 136 token; 'Hàng điện tử'(61<80) + 'Hoàn tiền' → 121 token
          out: 4 Chunk mới, chunk_id mới (vì version=2 nằm trong hash), ví dụ '0a1ca18b30d10659'
      → embeddings.embed(4 embed_text)  → 487 token
      → Qdrant: DELETE points where doc_id='return_policy' (4 chunk v1) → UPSERT 4 chunk v2
      → Postgres documents: version=2;  Redis HSET doc:version return_policy 2
      out: 4
    → cache.invalidate_doc('return_policy')
        Redis SMEMBERS cache:doc:return_policy → 4 entry
        → cache.delete(entry_id) ×4:  SREM khỏi mọi cache:doc:* trong provenance; DEL cache:entry:…; ZREM cache:lru; xoá vector Qdrant
        Redis DEL cache:doc:return_policy; HINCRBY cache:stats invalidated_doc_update 4
      out: ['89b29268-…', '13c22a20-…', '58268469-…', '09176751-…']      ← có cả câu trả lời VIP của cskh1 (mục 13 điểm 1)
    → sync.record_event(kind='doc_update', source='admin_api',
          summary='return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details={from_version:1, to_version:2, chunks:4, invalidated_entries:[…], actor:'admin_ops'})
```
Kể cả khi **không** xoá kịp (ví dụ entry được tạo đồng thời), điều kiện (4b) `_stale_docs` vẫn chặn, vì version trong provenance (1) khác version hiện tại (2).

---

## 10. Luồng G: Console đọc số liệu, stream, khôi phục demo
**GET /api/console/metrics/overview** ([09_metrics](walkthrough/raw/09_metrics.md), 34 ms): `auth.console_user` → `main.console_overview` → `metrics.overview(minutes=1440)`, chạy 4 câu SQL trên `traces` và đọc thêm từ Redis/Postgres:
- `totals`: đếm theo status, tổng token, chi phí, số lượt `unauthorized`, feedback.
- `latency`: p50/p95 theo status (`percentile_cont`).
- `series`: số request/hit/miss theo phút. `by_intent`: theo intent.
- `cache.stats()`: số entry, số entry bị xoá do sửa tài liệu, số entry bị loại do LRU (Redis).
- `access.partitions()`: `sig:known` → {signature: [username]}.
- `revocation_stats()`: trung bình/tối đa (effective_at − occurred_at) của `security_events`.

**GET /api/console/stream?token=…** (SSE): `auth.console_user_from_query`, vì EventSource của trình duyệt không gửi được header, nên token đi qua query. Sau đó backend subscribe Redis kênh `semcache:events` và đẩy từng message `trace` / `audit` / `security` xuống trình duyệt; mỗi giây không có tin thì gửi `ping`.

**POST /api/console/admin/reset** ([10_reset](walkthrough/raw/10_reset.md), 819 ms):
1. Với mỗi user trong `acl.yaml`: `find_user` + `user_realm_roles` (14 lời gọi Keycloak), rồi `set_realm_role` cho phần chênh lệch (ở lần chạy này: cấp lại `cskh_agent` cho cskh1).
2. `documents.list_documents()`: tài liệu nào không ở version nhỏ nhất thì `ingest(doc, 1)` (return_policy về v1).
3. `cache.flush()`: xoá mọi khoá `cache:*`, xoá và tạo lại collection Qdrant `semantic_cache`.
4. `access.invalidate_all()`, `DEL sig:known`.

Sau đó thread poller nhận event CREATE role mapping và xoá signature của cskh1 lần nữa (thừa nhưng vô hại).

**Các endpoint Console khác** (không có trong bản ghi vì chỉ đọc dữ liệu đơn giản): `console_traces` → `metrics.traces` (SELECT có lọc status/username); `console_trace` → `metrics.trace`; `console_cache_entries` → `cache.list_entries` + `cache.stats` + `access.partitions`; `console_cache_flush` → `cache.flush`; `console_security` → `metrics.security_events` + `revocation_stats` + các trace `unauthorized`; `admin_users` → với mỗi user: `find_user`, `user_realm_roles`, `list_accessible_collections` (gọi IAM thật, ngay lúc đó), đọc signature đang cache; `admin_documents` → `documents.list_documents`.

---

## 11. Các kiểu dữ liệu (dataclass) và ý nghĩa từng trường

**`iam.base.UserContext`**: người đang gọi, giải mã từ token.
| Trường | Ý nghĩa | Ví dụ |
|---|---|---|
| `user_id` | `sub` trong token, id user trong Keycloak | `829671b9-…` |
| `username` | `preferred_username` | `cskh1` |
| `roles` | role **trong token** (có thể cũ tới 15 phút) | `('employee','cskh_agent',…)` |
| `display_name` | `name` | `Lan CSKH` |

**`access.Signature`**: `signature` (hash 16 ký tự = mã partition), `collections` (danh sách collection **không** namespace, dùng để lọc Qdrant), `computed_at` (epoch), `from_cache` (lấy từ Redis hay vừa hỏi IAM).

**`classifier.Classification`**: `policy` (NORMAL/SHORT_TTL/NO_CACHE/BYPASS), `reason` (vì sao), `intent`, `intent_similarity`, `entities` (dict loại → giá trị).

**`retrieval.Retrieved`**: một đoạn tài liệu tìm được: `label` (c1…, gán trong `format_context`), `chunk_id`, `doc_id`, `version`, `collection`, `title`, `section_path`, `text`, `score` (cosine).

**`llm.LLMResult`**: `text`, `tokens_in`, `tokens_out`, `latency_ms` (chỉ thời gian chờ Gemini), `model`, `prompt_version`.

**`cache.Provenance`**: `chunk_id, doc_id, version, collection, title, section_path`. Đây là nguồn gốc của câu trả lời; dùng cho điều kiện (4b), reverse index và (6).

**`cache.CacheEntry`**
| Trường | Ý nghĩa / dùng ở đâu |
|---|---|
| `entry_id` | UUID; cũng là id point trong Qdrant |
| `partition` | signature lúc tạo; điều kiện (1) |
| `question` | câu hỏi gốc (vector của nó nằm ở Qdrant) |
| `answer`, `citations` | trả lại nguyên văn khi HIT |
| `provenance` | danh sách `Provenance`; điều kiện (4b), (6), reverse index |
| `intent`, `entities` | ngưỡng theo intent, điều kiện (3) |
| `policy` | NORMAL/SHORT_TTL → quyết định `ttl` |
| `prompt_version` | điều kiện (4a) |
| `model` | model đã sinh câu trả lời (để biết, chưa dùng làm điều kiện) |
| `created_at`, `ttl` | điều kiện (5); Redis cũng tự hết hạn theo `ttl` |
| `gen_tokens_in/out`, `gen_cost_usd`, `gen_latency_ms` | chi phí đã bỏ ra; mỗi HIT được tính là tiết kiệm từng ấy |
| `hits`, `last_hit` | số lần dùng lại; LRU |

**`cache.Candidate`**: một entry ứng viên khi tra: `entry_id, question, similarity, threshold, passed, reason`.
**`cache.LookupResult`**: `hit` (CacheEntry hoặc None), `similarity` (của ứng viên trúng, hoặc cao nhất nếu MISS), `candidates`.
**`pipeline.ChatResult`**: `trace_id, status, answer, citations, latency_ms, policy, similarity`.
**`tracing.Trace`**: `id`, `spans` (danh sách {name, title, start_ms, duration_ms, status, data}), `fields` (status, partition, intent, token, chi phí, …, được ghi thành cột của bảng `traces`).
**`iam.base.AccessChangeEvent`**: `occurred_at, kind (role_mapping/user_attribute/policy), summary, user_ids, affects_all, raw`.
**`chunking.Chunk`**: `chunk_id, doc_id, version, collection, title, section_path, text, embed_text, index`.

---

## 12. Danh mục toàn bộ hàm/class
Cột "Gọi bởi" chỉ ghi nơi gọi chính.

### `main.py` (endpoint)
| Hàm | Input → Output | Gọi bởi / ghi chú |
|---|---|---|
| `lifespan(app)` | – | uvicorn khi khởi động (mục 3) |
| `health()` | → `{ok, sync_last_poll, sync_error}` | kiểm tra thread đồng bộ |
| `me(user)` | → thông tin user + signature + collections | frontend khi tải trang (mục 4.0) |
| `_own_session(session_id, user)` | → dòng session hoặc 404 | chat, session_messages, delete_session |
| `chat(body, bg, user)` | `ChatIn` → JSON câu trả lời | mục 4 |
| `sessions(user)` / `session_messages(id, user)` / `delete_session(id, user)` | lịch sử chat của chính user | frontend |
| `feedback(message_id, body, user)` | `{value: -1/0/1}` → ghi vào `messages` và `traces` | nút 👍/👎 |
| `console_overview`, `console_traces`, `console_trace`, `console_cache_entries`, `console_cache_flush`, `console_security`, `console_stream` | xem mục 10 | Console |
| `_acl()` | → dict từ `acl.yaml` | các endpoint admin |
| `admin_users`, `admin_set_role`, `admin_documents`, `admin_publish`, `admin_reset` | xem mục 8, 9, 10 | Console → Quản trị |
| `ChatIn, FeedbackIn, RoleIn, PublishIn, ResetIn` | model kiểm tra body request (pydantic) | |

### `auth.py`
| Hàm | Input → Output |
|---|---|
| `_jwks()` | → `PyJWKClient` trỏ tới `/realms/semcache/protocol/openid-connect/certs` (cache) |
| `issuer()` | → `'{KEYCLOAK_PUBLIC_URL}/realms/semcache'` |
| `decode(token)` | JWT → `UserContext`; sai chữ ký/iss/azp → 401 |
| `current_user(request)` | header Bearer → `UserContext` |
| `console_user(user)` | cần `ops_admin` trong `user.roles` (role của token) → 403 |
| `console_user_from_query(token)` | như trên nhưng token lấy từ query (SSE) |

### `pipeline.py`
| Hàm | Input → Output |
|---|---|
| `answer(user, question, session_id, history, tr)` | → `(ChatResult, Trace)`; 8 bước, mục 4 |
| `_citations(answer, chunks)` | tìm `[cN]` → danh sách citation (không trùng) |
| `no_answer_text()` | → câu "không tìm thấy" từ prompts.yaml |
| `ChatResult` | dataclass, mục 11 |

### `access.py`
| Hàm | Input → Output |
|---|---|
| `adapter()` | → `KeycloakAccessControl` (một instance, lru_cache) |
| `compute_hash(namespaced)` | list `ns:collection` → hash 16 ký tự (có `signature_scheme_version`) |
| `get(user)` | → `Signature` (Redis, hoặc `refresh`) |
| `refresh(user)` | hỏi IAM → tính hash → ghi Redis (TTL 300 s) + `sig:known` |
| `invalidate(user_id)` / `invalidate_all()` | xoá signature trong Redis |
| `partitions()` | → {signature: [username]} cho Console |
| `_key(user_id)` | → `'sig:user:<id>'` |

### `iam/base.py`, `iam/keycloak.py`, `iam/stubs.py`
| Hàm/Class | Input → Output |
|---|---|
| `AccessControlBase` | interface: `list_accessible_collections(user) → set`, `check_collections(user, set) → dict`, `context_attributes() → list` |
| `ChangeEventSource` | interface: `poll() → list[AccessChangeEvent]` |
| `KeycloakAdmin.__init__` | đọc cấu hình realm/client/secret |
| `.token()` | client_credentials → access token service account (cache, có lock) |
| `.request(method, path, **kw)` | gọi `/admin/realms/semcache{path}` kèm token; lỗi HTTP → exception |
| `.client_uuid()` | uuid client backend (cache) |
| `.find_user(username)` / `.list_users()` / `.user_realm_roles(user_id)` / `.realm_role(name)` | đọc user/role |
| `.set_realm_role(user_id, role, grant)` | POST/DELETE role mapping |
| `.evaluate(user_id, resource_names=None)` | → `{resource: bool}` (mục 1.3) |
| `.resources()` | → `{tên resource: _id}` (cache 60 s) |
| `.admin_events(max_results=200)` | → danh sách admin event mới nhất |
| `KeycloakAccessControl.list_accessible_collections(user)` | evaluate tất cả → set collection được PERMIT |
| `KeycloakAccessControl.check_collections(user, cols)` | evaluate các resource tương ứng; lỗi → tất cả False |
| `_event_key(e)` | khoá chống trùng cho event không có id |
| `KeycloakEventSource.poll()` | event mới → `AccessChangeEvent` (mục 1.4) |
| `GCPAccessControl`, `AWSAccessControl`, `NotImplementedEventSource` | khung mở rộng, chưa cài đặt |

### `embeddings.py`, `llm.py`, `prompts.py`
| Hàm | Input → Output |
|---|---|
| `embeddings.model()` / `_key(text)` | tên model / khoá Redis `emb:<model>:<sha1>` |
| `embeddings.embed(texts)` | → `(vectors chuẩn hoá L2, token tính phí, hit hết cache?)` |
| `embeddings.embed_one(text)` | 1 câu |
| `embeddings.dim()` | số chiều vector (gọi embed 1 câu thử) |
| `llm.model()` / `llm.cost_usd(in, out, embed)` | tên model / chi phí ước tính theo `settings.pricing` |
| `llm.generate(prompt_name, **variables)` | → `LLMResult`; thử lại 3 lần |
| `prompts._all()` | đọc cả `configs/prompts.yaml` một lần (lru_cache) |
| `prompts.get(name)` / `text(name)` / `variables(name)` | đọc prompt / chuỗi / tập biến `{x}` |
| `prompts.render(name, **kw)` | → `(system, user)`; thiếu biến → `PromptError` |
| `prompts.version(name)` | → `'v1-<hash8>'` |
| `prompts.validate(required)` | kiểm tra lúc khởi động |

### `classifier.py`
| Hàm | Input → Output |
|---|---|
| `normalize(text)` | chữ thường, gộp khoảng trắng |
| `_has(text, words)` | từ khoá đầu tiên khớp hoặc None |
| `cache_policy(question)` | → `(policy, reason)` theo thứ tự NO_CACHE → BYPASS → SHORT_TTL → NORMAL |
| `_intent_centroids()` | embed câu mẫu → vector trung bình mỗi intent (cache trong tiến trình) |
| `intent(vec)` | → `(intent, similarity)` hoặc `('default', s)` nếu < 0.45 |
| `extract_entities(question)` | → `{loại: giá trị}` (ưu tiên cụm dài hơn) |
| `classify(question, vec)` | gộp 3 hàm trên → `Classification` |

### `cache.py`
| Hàm | Input → Output |
|---|---|
| `ensure_collection()` | tạo Qdrant `semantic_cache` + index `partition` |
| `threshold_for(intent)` | ngưỡng theo intent hoặc mặc định 0.75 |
| `get_entry(id)` | Redis → `CacheEntry` hoặc None |
| `lookup(vec, partition, intent, entities, prompt_version, reverify)` | → `LookupResult` (mục 5) |
| `_stale_docs(e)` | danh sách tài liệu đã đổi version |
| `_touch(e)` | tăng `hits`, cập nhật LRU |
| `store(e, vec)` | ghi Qdrant + Redis + reverse index, rồi `evict_if_needed` |
| `new_entry_id()` | UUID |
| `delete(id)` / `_delete_vector(id)` | xoá entry khỏi Redis (kể cả reverse index) và Qdrant |
| `invalidate_doc(doc_id)` | xoá mọi entry dùng tài liệu → list id |
| `evict_if_needed()` | LRU khi vượt `max_entries` |
| `list_entries(limit)` / `stats()` / `flush()` | cho Console / khôi phục demo |
| `CacheEntry.to_json()` / `from_json(s)` | tuần tự hoá Redis |

### `retrieval.py`, `documents.py`, `chunking.py`
| Hàm | Input → Output |
|---|---|
| `retrieval.search(vec, collections, top_k)` | Qdrant có filter → `list[Retrieved]` |
| `retrieval.format_context(chunks)` | gán nhãn c1… → chuỗi context |
| `documents.docs_dir()` / `file_for(id, v)` / `parse_file(path)` | đường dẫn / tách front matter |
| `documents.available_versions()` | quét file → {doc_id: {title, collection, versions}} |
| `documents.ensure_collection()` | tạo Qdrant `chunks` + index `collection`, `doc_id` |
| `documents.current_version(id)` / `current_versions(ids)` | Redis `doc:version` (rơi về Postgres nếu thiếu) |
| `documents.ingest(id, v)` | mục 2 / 9 → số chunk |
| `documents.ingest_all_initial()` | nạp version nhỏ nhất của mọi tài liệu (seed) |
| `documents.list_documents()` | cho Console |
| `chunking.ntokens(text)` / `_enc()` | đếm token bằng tiktoken cl100k |
| `chunking._sections(md, title)` | tách theo tiêu đề → `_Section(path, lines)` |
| `chunking._split_long(body, max, overlap)` | tách mục dài (bảng: lặp header; văn bản: theo đoạn + overlap) |
| `chunking.chunk_document(...)` | → `list[Chunk]` |

### `sync.py`, `tracing.py`, `audit.py`, `metrics.py`, hạ tầng
| Hàm | Input → Output |
|---|---|
| `sync.PermissionSync.__init__/start/stop/_run/poll_once` | thread đồng bộ (mục 8.2) |
| `sync.record_event(...)` | INSERT `security_events` + publish → dict |
| `sync.publish_document_version(doc_id, v, actor)` | mục 9 |
| `sync._now()` | thời điểm UTC |
| `tracing.Trace.__init__/span/set/elapsed_ms/save` | mục 4.4 |
| `tracing.summary(id)` / `jsonable(row)` / `publish(kind, data)` | tóm tắt trace / đổi kiểu cho JSON / Redis PUBLISH |
| `audit.canaries()` / `find(text)` / `run(trace_id, user, answer)` | mục 4.5 |
| `metrics.overview/revocation_stats/traces/trace/security_events` | mục 10 |
| `config.env()/settings()/classifier_config()/data_dir()/load_yaml()/_expand()`, class `Env` | đọc `.env` (→ dataclass `Env`: key API, địa chỉ hạ tầng) và YAML; `${VAR:default}` |
| `db.pool()/conn()/init_schema()/fetch_all()/fetch_one()/execute()` | Postgres |
| `clients.rds()/qdrant()/openai_client()/gemini_client()` | kết nối dùng chung (tạo một lần) |

---

## 13. Các điểm có thể chưa hợp lý
Mỗi điểm có **bằng chứng** từ bản ghi, **mức độ**, và **hướng sửa**. Mức độ: 🔴 ảnh hưởng đúng/sai hoặc bảo mật · 🟠 ảnh hưởng hiệu quả hoặc độ chính xác · 🟡 nhỏ.

1. 🟠 **Provenance gồm mọi chunk trong context, kể cả chunk không được trích dẫn, nên bị xoá oan nhiều.** Câu trả lời VIP chỉ trích dẫn `c2` (`vip_return_exception`), nhưng provenance có cả `return_policy`, `membership_faq`, `complaint_handling`. Khi xuất bản `return_policy` v2, entry `13c22a20` bị xoá (mục 9) dù nội dung không đổi.
   *Đánh đổi:* cách hiện tại an toàn hơn, vì LLM có thể dùng một chunk mà không trích dẫn nó. *Hướng sửa:* lưu hai tập. Tài liệu được trích dẫn đổi thì xoá ngay; tài liệu chỉ có trong context đổi thì đánh dấu "cần kiểm tra lại". Hoặc giảm `top_k`/tăng `min_score` để context ít nhiễu hơn. Nên đưa vào thí nghiệm của Giai đoạn C.
2. 🟠 **Header path của chunk gộp chỉ giữ tên mục đầu.** Chunk `232c157b…` mang nhãn "Phạm vi áp dụng" nhưng chứa fact "Thời hạn đổi trả… 7 ngày". Trong luồng A, chunk "Khách hạng Bạc" (đã gộp với "Lưu ý bảo mật… thời hạn ngoại lệ") **xếp hạng 1 (0.7714), cao hơn chunk VIP (0.7577)**. *Hướng sửa:* path của chunk gộp ghi đủ tên các mục; lưu `index`; đánh giá lại bằng fact recall@k (Giai đoạn B).
3. 🟠 **Chi phí khởi động lạnh nằm trong request đầu tiên.** `_intent_centroids` mất 460–570 ms qua các lần chạy (embed 16 câu mẫu), lần đầu tạo Gemini client khoảng 600–700 ms (`llm.generate` 3772 ms so với Gemini 3056 ms), lần đầu nạp tiktoken trong `chunk_document` 440–490 ms, `classifier_config` 20 ms. *Hướng sửa:* làm nóng sẵn trong `lifespan`. Nếu không, số liệu latency của các request đầu trong thí nghiệm sẽ bị lệch.
4. 🟠 **Thời gian của HIT chủ yếu là gọi OpenAI để embed câu hỏi** (HIT 915 ms, trong đó embed 844 ms; tra cache 39 ms, gồm cả reverify 17 ms; ở lần chạy trước HIT 340 ms, embed 243 ms, nên thời gian OpenAI dao động mạnh). Cache embedding chỉ có tác dụng khi câu hỏi giống hệt từng chữ. Đây là giới hạn cần nêu khi đánh giá latency; có thể cân nhắc embedding chạy cục bộ.
5. 🟡 **Reverify (điều kiện 6) gọi Keycloak cho từng ứng viên vượt qua các điều kiện trước.** Hiện tối đa 3 ứng viên, mỗi lần khoảng 30 ms. Có thể gom lại một lần gọi cho mọi ứng viên, hoặc cache quyết định khoảng 1–2 s.
6. 🟡 **Poller lấy `max=200` event mới nhất mỗi lần.** Nếu có hơn 200 thay đổi giữa hai lần poll (đổi quyền hàng loạt) thì sẽ sót event; khi đó chỉ còn TTL 300 s và reverify bảo vệ. *Hướng sửa:* phân trang bằng `first`/`dateFrom`, hoặc khi thấy đủ 200 event thì coi là `affects_all`.
7. 🟡 **Câu NO_CACHE/BYPASS vẫn chạy retrieval và LLM bình thường** (đúng ý đồ). Nhưng câu cá nhân kiểu "đơn hàng của tôi" thì kho tài liệu không bao giờ trả lời được, nên luôn tốn khoảng 700 token cho một câu "không tìm thấy". Có thể chuyển hướng sang hệ thống khác (ngoài phạm vi).
8. 🟡 **Câu "không tìm thấy" phụ thuộc LLM chép đúng nguyên văn** (`no_answer_text() in ans`). Nếu Gemini diễn đạt khác, câu trả lời rỗng nội dung vẫn có thể được cache (với điều kiện có trích dẫn). Có thể kiểm tra thêm bằng việc câu trả lời không có trích dẫn nào.
9. 🔴 **Quyền vào Console kiểm tra bằng role trong token, không hỏi IAM.** `auth.console_user` dùng `user.roles` lấy từ token sống 15 phút. Thu hồi `ops_admin` thì người đó vẫn vào được Console tối đa 15 phút. Điều này không ảnh hưởng tài liệu người dùng đọc được (phần đó luôn hỏi IAM), nhưng không nhất quán với nguyên tắc "IAM là trọng tài". *Hướng sửa:* tạo resource `console` trong Keycloak và dùng `evaluate`, hoặc giảm thời gian sống của token.
10. 🟡 **Khôi phục demo gọi Keycloak 2 lần cho mỗi user và sinh event thừa.** Chỉ ảnh hưởng demo/test, không ảnh hưởng luồng chính.
11. 🟡 **Gọi lặp trong pipeline:** `cache.threshold_for` 2 lần, `llm.cost_usd` 3 lần, `prompts.get` nhiều lần. Không đáng kể về thời gian, chỉ ảnh hưởng độ gọn của code.
12. 🟡 **`main.chat` lưu tin nhắn của user trước khi chạy pipeline.** Nếu pipeline lỗi (502), session có câu hỏi mà không có câu trả lời. Trace lỗi vẫn được lưu với status ERROR. Có thể chấp nhận; nếu muốn thì lưu một tin nhắn lỗi cho assistant.
