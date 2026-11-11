# Từ điển khái niệm (DICTIONARY)

Tra nhanh các từ khoá, tên biến, tên trường, khoá lưu trữ dùng trong code và trong [WALKTHROUGH.md](WALKTHROUGH.md). Mỗi mục gồm: **Là gì**, **Ví dụ thật** (lấy từ hệ thống đang chạy, lần chạy 11/11/2026), **Ở đâu** trong code, và **Liên quan**.

- Cách tra: Ctrl+F tên cần tìm, hoặc xem bảng tra nhanh bên dưới.
- Bổ sung: khi bạn hỏi "X là gì", câu trả lời sẽ được thêm vào đây. Những mục thêm theo câu hỏi của bạn có dòng *Thêm … theo câu hỏi của bạn*.
- Đường dẫn code tính từ `backend/app/`.

## Mục lục
1. [Khái niệm thiết kế](#1-khái-niệm-thiết-kế)
2. [Keycloak / IAM](#2-keycloak--iam)
3. [Tham số & biến trong code](#3-tham-số--biến-trong-code)
4. [Kiểu dữ liệu & trường](#4-kiểu-dữ-liệu--trường)
5. [Nơi lưu trữ (Redis, Qdrant, Postgres)](#5-nơi-lưu-trữ-redis-qdrant-postgres)
6. [Trạng thái & nhãn](#6-trạng-thái--nhãn)
7. [Cấu hình](#7-cấu-hình)

## Bảng tra nhanh
| Từ khoá | Nhóm |
|---|---|
| access signature, admission, audit, BYPASS, cache entry, canary, candidate, centroid, chunk, citation, collection, cold start, defense-in-depth, entity, eviction, fail-closed, hard negative, intent, invalidation, namespace, partition, post-verify, pre-filter, provenance, revocation window, reverse index, reverify, semantic cache, similarity, threshold, trace, span, TTL, unauthorized serve | [1](#1-khái-niệm-thiết-kế) |
| ABAC, admin event, azp, client, client uuid, decisionStrategy, evaluate, fetchRoles, iss, JWKS, PERMIT/DENY, permission, PKCE, policy (Keycloak), preferred_username, protocol mapper, RBAC, realm, realm_access, realm role, resource, service account, sub, token, user attribute | [2](#2-keycloak--iam) |
| actor, affects_all, cols, collections, entities, grant, history, label, last_ms, max_results, namespaced, partition (tham số), prompt_name, prompt_version, resource_names, since_ms, top_k, min_score, tr, user, user_id, variables, vec | [3](#3-tham-số--biến-trong-code) |
| AccessChangeEvent, CacheEntry, Candidate, ChatResult, Chunk, Classification, LLMResult, LookupResult, Provenance, Retrieved, Signature, Trace, UserContext | [4](#4-kiểu-dữ-liệu--trường) |
| cache:entry, cache:doc, cache:lru, cache:stats, chunks, doc:version, documents, emb:, messages, security_events, semantic_cache, semcache:events, sessions, sig:known, sig:user, traces | [5](#5-nơi-lưu-trữ-redis-qdrant-postgres) |
| HIT, MISS, NO_CACHE, BYPASS, ERROR, NORMAL, SHORT_TTL, tên span (identity … admission), permission_change, doc_update, role_mapping | [6](#6-trạng-thái--nhãn) |
| threshold_default, ttl_seconds, max_entries, candidates, reverify_iam_on_hit, signature_ttl_seconds, event_poll_seconds, signature_scheme_version, top_k, min_score, chunking, pricing, classifier.yaml, prompts.yaml, .env | [7](#7-cấu-hình) |

---

## 1. Khái niệm thiết kế

### access signature (signature)
**Là gì:** mã hash 16 ký tự đại diện cho **tập collection mà một user được đọc** (theo Keycloak, tại lúc tính). Hai user có cùng signature thì đọc được đúng cùng một tập tài liệu.
**Ví dụ thật:** cskh1 đọc `{cskh, internal_all, public}` → `95503c7831d2f7ed`; khach đọc `{public}` → `3963a48f4b463545`; cskh1 sau khi bị thu hồi `cskh_agent` → `1fb84ec24c927b56`.
**Ở đâu:** `access.compute_hash`, `access.refresh`; cách tính: `sha256("v1|keycloak:cskh,keycloak:internal_all,keycloak:public")[:16]`.
**Liên quan:** partition, namespace, `sig:user`, `signature_scheme_version`.

### admission
**Là gì:** bước quyết định **có lưu câu trả lời vào cache không** (bước 8 của pipeline). Không lưu nếu: câu hỏi NO_CACHE/BYPASS; không có ngữ cảnh; câu trả lời là "không tìm thấy"; không có trích dẫn hợp lệ.
**Ví dụ thật:** câu "Đơn hàng của tôi đang ở đâu rồi?" có `admitted=False` với 3 lý do (chính sách NO_CACHE, câu trả lời "không tìm thấy", không có trích dẫn).
**Ở đâu:** cuối `pipeline.answer`, span `admission`.
**Liên quan:** cache entry, citation, NO_CACHE.

### audit
**Là gì:** kiểm tra **sau khi đã trả lời** (chạy nền) xem câu trả lời có chứa canary của collection mà user không có quyền hay không.
**Ví dụ thật:** `{canaries: [vip_33, vip_47], denied_collections: [], checked_with_iam: True}` → `unauthorized=False`.
**Ở đâu:** `audit.run`, được gọi bằng `BackgroundTasks` trong `main.chat`; kết quả ghi vào cột `traces.audit`.
**Liên quan:** canary, unauthorized serve.

### cache entry
**Là gì:** một câu trả lời đã lưu trong semantic cache, kèm mọi thông tin để quyết định có dùng lại được không.
**Ví dụ thật:** entry `13c22a20-a6b2-4a03-9448-46772e13273d` cho câu "Khách VIP được đổi trả trong bao lâu?" ở partition `95503c7831d2f7ed`.
**Ở đâu:** class `cache.CacheEntry`; lưu ở Redis `cache:entry:<id>` (nội dung) và Qdrant `semantic_cache` (vector câu hỏi).
**Liên quan:** CacheEntry (nhóm 4), provenance, partition.

### canary
**Là gì:** một **giá trị đặc trưng chỉ có trong tài liệu mật** (con số, mã). Thấy nó trong câu trả lời gửi cho người không có quyền nghĩa là có rò rỉ. Cách phát hiện là so khớp regex, cho kết quả chắc chắn, không cần LLM chấm.
**Ví dụ thật:** `vip_33` (collection cskh, regex `\b33\s*ngày`), `n_c1` (sales_north, `12[,.]5\s*%`).
**Ở đâu:** `data/pilot/canaries.yaml`; `audit.canaries`, `audit.find`.
**Liên quan:** audit, unauthorized serve.

### candidate (ứng viên cache)
**Là gì:** một entry mà Qdrant trả về khi tra cache (tối đa 3, cùng partition), được kiểm tra lần lượt qua các điều kiện hit.
**Ví dụ thật:** `Candidate(entry_id='13c22a20-…', question='Khách VIP được đổi trả trong bao lâu?', similarity=0.8471, threshold=0.75, passed=True, reason='thoả mọi điều kiện')`.
**Ở đâu:** `cache.lookup`; class `cache.Candidate`.
**Liên quan:** Candidate.reason (nhóm 4), threshold.

### centroid (intent)
**Là gì:** vector trung bình của các câu mẫu của một intent. Intent của câu hỏi là intent có centroid gần vector câu hỏi nhất.
**Ví dụ thật:** 8 centroid từ 16 câu mẫu (236 token embedding), tính một lần khi có câu hỏi đầu tiên (khoảng 0,5 s).
**Ở đâu:** `classifier._intent_centroids`; câu mẫu trong `configs/classifier.yaml` → `intent.examples`.
**Liên quan:** intent, cold start.

### chunk
**Là gì:** một đoạn tài liệu sau khi cắt, đơn vị để tìm kiếm. Không bao giờ vượt ranh giới tài liệu.
**Ví dụ thật:** `chunk_id='232c157bca68b49d'`, `section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'`, 136 token.
**Ở đâu:** `chunking.chunk_document`; lưu ở Qdrant `chunks`.
**Liên quan:** Chunk (nhóm 4), provenance.

### citation (trích dẫn)
**Là gì:** nhãn `[c1]`, `[c2]`… mà LLM ghi sau mỗi ý, trỏ tới đoạn ngữ cảnh đã dùng. Backend đổi nhãn thành thông tin tài liệu.
**Ví dụ thật:** `[{label:'c2', doc_id:'vip_return_exception', section:'… > Thời hạn đổi trả của khách VIP', collection:'cskh', version:1}]`.
**Ở đâu:** `pipeline._citations`; nhãn gán trong `retrieval.format_context`.
**Liên quan:** label, admission.

### collection
**Là gì:** **đơn vị phân quyền**: một nhóm tài liệu có cùng quyền đọc. Mỗi tài liệu thuộc đúng một collection.
**Ví dụ thật:** `public`, `internal_all`, `cskh`, `hr_confidential`, `sales_north`, `sales_south`.
**Ở đâu:** khai báo trong `data/pilot/acl.yaml`; mỗi collection là một resource `collection:<id>` trong Keycloak; payload `collection` của chunk trong Qdrant.
**Liên quan:** resource (nhóm 2), access signature, pre-filter.

### cold start (khởi động lạnh)
**Là gì:** chi phí chỉ xảy ra **lần đầu** trong một tiến trình backend, vì có thứ được tạo lười rồi cache lại.
**Ví dụ thật:** tính centroid intent khoảng 0,5 s; tạo Gemini client khoảng 0,6–0,7 s; nạp tiktoken khoảng 0,45 s.
**Ở đâu:** các hàm có `@lru_cache` (`_intent_centroids`, `gemini_client`, `_enc`…).
**Liên quan:** WALKTHROUGH mục 13 điểm 3.

### defense-in-depth (nhiều lớp bảo vệ)
**Là gì:** không dựa vào một cơ chế duy nhất để chặn rò rỉ. Ở đây có các lớp: partition → reverify khi hit → pre-filter → post-verify → audit.
**Ví dụ thật:** ngày 10/11, poller lỗi không nhận event thu hồi quyền, nhưng reverify vẫn chặn được entry cũ.
**Liên quan:** reverify, post-verify, fail-closed.

### entity
**Là gì:** thực thể cụ thể trong câu hỏi (gói, miền, hạng khách) nhận ra bằng từ điển. Hai câu khác entity thì **không được** dùng chung cache, dù rất giống nhau.
**Ví dụ thật:** "Giá gói … Bạc …" → `{'package': 'bac'}`; "Khách VIP …" → `{'tier': 'vip'}`.
**Ở đâu:** `classifier.extract_entities`; từ điển ở `configs/classifier.yaml` → `entities`.
**Liên quan:** hard negative, điều kiện hit (3).

### eviction (loại bỏ)
**Là gì:** xoá entry khi cache đầy. Hiện dùng **LRU**: bỏ entry lâu không được dùng nhất.
**Ví dụ thật:** `max_entries=5000`, pilot chưa bao giờ đầy (`evict_if_needed()` trả `[]`).
**Ở đâu:** `cache.evict_if_needed`; thứ tự LRU ở Redis `cache:lru`.
**Liên quan:** invalidation (khác: invalidation xoá vì dữ liệu đổi, eviction xoá vì đầy).

### fail-closed
**Là gì:** khi hệ thống quyền gặp lỗi thì **từ chối** truy cập, thay vì cho phép.
**Ở đâu:** `KeycloakAccessControl.check_collections` bắt exception → mọi collection `False`.
**Liên quan:** post-verify.

### hard negative
**Là gì:** cặp câu hỏi **rất giống nhau về chữ nhưng đáp án khác**. Dùng để kiểm tra cache có hit nhầm không.
**Ví dụ thật:** "Giá gói bảo hành mở rộng Bạc…" và "…Vàng…": similarity **0.84**, cao hơn nhiều cặp diễn đạt lại thật (thấp nhất 0.57).
**Liên quan:** entity, threshold.

### intent
**Là gì:** nhóm chủ đề của câu hỏi, dùng để chọn ngưỡng similarity riêng (nếu có) và để thống kê trên Console.
**Ví dụ thật:** `('return_policy', 0.72)`; dưới `min_similarity` 0.45 thì là `default`.
**Ở đâu:** `classifier.intent`.
**Liên quan:** centroid, threshold.

### invalidation (vô hiệu hoá)
**Là gì:** làm một thứ đang cache không còn được dùng vì dữ liệu gốc đã đổi. Có hai loại:
(1) xoá **signature** của user khi quyền đổi (`access.invalidate`);
(2) xoá **cache entry** khi tài liệu đổi version (`cache.invalidate_doc`).
**Ví dụ thật:** xuất bản `return_policy` v2 → xoá 4 entry (`89b29268-…`, `13c22a20-…`, `58268469-…`, `09176751-…`).
**Liên quan:** reverse index, revocation window, eviction.

### namespace
**Là gì:** tiền tố nguồn IAM gắn trước tên collection khi tính signature, để sau này thêm IAM khác (GCP/AWS) không bị trùng tên.
**Ví dụ thật:** `keycloak:public`.
**Ở đâu:** `KeycloakAccessControl.namespace = "keycloak"`, dùng trong `access.refresh`.
**Liên quan:** access signature, namespaced (nhóm 3).

### partition
**Là gì:** **vùng của cache** dành cho một access signature. Tra cache chỉ tìm trong partition của người hỏi. Giá trị partition chính là signature.
**Ví dụ thật:** `95503c7831d2f7ed` (cskh1, cskh2 dùng chung), `3963a48f4b463545` (khach).
**Ở đâu:** payload `partition` của Qdrant `semantic_cache`; trường `CacheEntry.partition`; cột `traces.partition`.
**Liên quan:** access signature.

### post-verify (iam_verify)
**Là gì:** sau khi tìm được các đoạn tài liệu, **hỏi lại Keycloak** quyền đọc collection của các đoạn đó. Đoạn bị từ chối thì loại khỏi ngữ cảnh.
**Ví dụ thật:** `check_collections(user, {'cskh','public'})` → `{'cskh': True, 'public': True}`.
**Ở đâu:** bước 6 của `pipeline.answer`, span `iam_verify`.
**Quan hệ với pre-filter:** output của bước 5 (các chunk) là input của bước 6 (collection của các chunk đó). Bước 5 dựa vào **ảnh chụp** quyền (signature trong Redis, có thể cũ tới 300 s); bước 6 hỏi **Keycloak ngay lúc đó**. Ảnh chụp rộng hơn thực tế (vừa bị thu hồi) thì bước 6 chặn chunk và xoá signature, nên không rò rỉ. Ảnh chụp hẹp hơn (vừa được cấp) thì tạm thiếu tài liệu, vì bước 6 chỉ loại bỏ chứ không thêm được. Bình thường bước 6 cho `blocked = []` (tốn khoảng 36 ms nhưng không đổi gì). Nhánh "chặn chunk" chưa có bản ghi thật.
**Liên quan:** pre-filter, evaluate, reverify (cặp tương tự trên đường HIT).
*Bổ sung 11/11/2026 theo câu hỏi của bạn.*

### pre-filter
**Là gì:** khi tìm đoạn tài liệu, Qdrant **chỉ tìm trong các collection user được đọc** (theo signature). PermRAG gốc thì tìm trên toàn bộ rồi mới lọc.
**Ví dụ thật:** filter `collection ∈ ['cskh','internal_all','public']`.
**Ở đâu:** `retrieval.search`.
**Vì sao cần:** nếu chỉ lọc sau (như PermRAG), user ít quyền nhận top-k toàn tài liệu mật bị chặn, nên gần như không có ngữ cảnh. Lọc trước đảm bảo đủ k chunk hợp lệ. Bước này tin vào ảnh chụp quyền, nên luôn đi kèm post-verify.
**Liên quan:** post-verify, collection, access signature.
*Bổ sung 11/11/2026 theo câu hỏi của bạn.*

### provenance (nguồn gốc)
**Là gì:** danh sách **các đoạn tài liệu (kèm version) đã nằm trong ngữ cảnh** khi sinh câu trả lời. Dùng để biết entry nào bị ảnh hưởng khi tài liệu đổi.
**Ví dụ thật:** entry VIP có 5 provenance: `vip_return_exception v1` ×2, `membership_faq v1`, `return_policy v1`, `complaint_handling v1`.
**Ở đâu:** `CacheEntry.provenance` (list `Provenance`).
**Liên quan:** reverse index, điều kiện hit (4b), WALKTHROUGH mục 13 điểm 1.

### reverse index
**Là gì:** chỉ mục ngược **tài liệu → các entry dùng nó**, để khi tài liệu đổi biết ngay cần xoá entry nào.
**Ví dụ thật:** Redis `cache:doc:return_policy` = {4 entry id}.
**Ở đâu:** ghi trong `cache.store`, đọc trong `cache.invalidate_doc`.
**Liên quan:** provenance, invalidation.

### reverify (điều kiện 6)
**Là gì:** khi một entry sắp được dùng lại, **hỏi Keycloak lần nữa** xem user còn quyền đọc các collection trong provenance không. Đây là lớp bảo vệ khi signature trong Redis có thể đã cũ.
**Ví dụ thật:** `reverify({'public','cskh'})` → `{public: True, cskh: True}` (17–32 ms).
**Ở đâu:** hàm `reverify` trong `pipeline.answer`, được gọi trong `cache.lookup`; bật/tắt bằng `reverify_iam_on_hit`.
**Liên quan:** defense-in-depth, evaluate.

### revocation window
**Là gì:** khoảng thời gian **từ lúc quyền bị thu hồi trong Keycloak đến lúc hệ thống áp dụng** (xoá signature). Trong khoảng đó, về lý thuyết user có thể dùng quyền cũ.
**Ví dụ thật:** 0,15 s (lần chạy 11/11) và 1,60 s (lần trước); dao động 0–2 s theo chu kỳ poll.
**Ở đâu:** `security_events.effective_at − occurred_at`; `metrics.revocation_stats`.
**Liên quan:** admin event, `event_poll_seconds`.

### semantic cache
**Là gì:** cache tra theo **ý nghĩa** câu hỏi (độ gần vector), không cần trùng chữ.
**Liên quan:** similarity, threshold, partition.

### similarity
**Là gì:** độ giống nhau giữa hai vector (cosine), từ khoảng −1 đến 1, càng cao càng giống.
**Ví dụ thật:** "Thời hạn đổi trả hàng cho khách VIP là bao lâu?" so với entry "Khách VIP được đổi trả trong bao lâu?" = **0.8471**.
**Liên quan:** threshold, hard negative.

### threshold (ngưỡng, τ)
**Là gì:** similarity tối thiểu để một entry được coi là "cùng câu hỏi".
**Ví dụ thật:** `0.75` (đo trên pilot; calibrate ở thí nghiệm E1).
**Ở đâu:** `cache.threshold_for`; cấu hình `threshold_default`, `threshold_by_intent`.

### trace / span
**Là gì:** **trace** là bản ghi một request; **span** là một bước trong request đó (tên, thời điểm bắt đầu, thời lượng, dữ liệu chi tiết). Console đọc trace để hiển thị trang chi tiết request.
**Ví dụ thật:** trace `69867628-…` có 8 span: identity, embed, classify, cache_lookup, retrieval, iam_verify, llm, admission.
**Ở đâu:** `tracing.Trace`, `Trace.span`; bảng Postgres `traces` (cột `spans` JSONB).
**Lưu ý:** khác với "bản ghi lời gọi hàm" trong `docs/walkthrough/raw/` (công cụ tài liệu, không phải tính năng của hệ thống).

### TTL (time to live)
**Là gì:** thời gian sống của một mục trong cache; hết TTL thì tự bị xoá.
**Ví dụ thật:** cache entry NORMAL 604800 s (7 ngày), SHORT_TTL 3600 s; signature 300 s; embedding 30 ngày.

### unauthorized serve
**Là gì:** một câu trả lời đã gửi cho user nhưng chứa thông tin user không có quyền xem (theo audit canary). Mục tiêu là luôn bằng 0.
**Ở đâu:** cột `traces.unauthorized`; Console → Tổng quan / Bảo mật.

---

## 2. Keycloak / IAM

### RBAC / ABAC
**Là gì:** RBAC phân quyền theo **vai trò** (role). ABAC phân quyền theo **thuộc tính** (attribute) của user/tài nguyên/ngữ cảnh.
**Ví dụ thật:** RBAC: `p_cskh` = có role `cskh_agent`. ABAC: `p_region_north` = attribute `region` khớp `^north$`.

### realm
**Là gì:** một "không gian" riêng trong Keycloak gồm user, role, client, policy.
**Ví dụ thật:** `semcache`.

### client
**Là gì:** một ứng dụng đăng ký với Keycloak.
**Ví dụ thật:**
- `semcache-frontend`: public client, trình duyệt đăng nhập qua đây (PKCE).
- `semcache-backend`: confidential client, có service account và bật Authorization Services (nơi chứa resource/policy/permission).

### client uuid
**Là gì:** id nội bộ của client (khác `clientId` là tên). Admin API cần id này trong đường dẫn.
**Ví dụ thật:** `b241a711-46be-488a-b226-d122149c1b86` (semcache-backend).
**Ở đâu:** `KeycloakAdmin.client_uuid()` (cache trong object).

### service account
**Là gì:** "tài khoản máy" của client backend, dùng để backend tự gọi Admin API (không cần mật khẩu admin).
**Ví dụ thật:** `service-account-semcache-backend`, có các role `realm-management`: `view-users, manage-users, view-events, manage-authorization, …`.
**Ở đâu:** `KeycloakAdmin.token()` (grant `client_credentials`).

### realm role
**Là gì:** vai trò gán cho user trong realm.
**Ví dụ thật:** `customer, employee, cskh_agent, hr, sales, ops_admin`; Keycloak tự thêm `default-roles-semcache, offline_access, uma_authorization`.

### user attribute
**Là gì:** thuộc tính tuỳ ý của user, dùng cho ABAC.
**Ví dụ thật:** `sales_bac.attributes = {'region': ['north']}`.

### resource
**Là gì:** "thứ cần bảo vệ" trong Authorization Services. Ở đây **mỗi collection là một resource**.
**Ví dụ thật:** `collection:cskh` (id `2d0c7fd6-1799-4bbb-a29c-9cde95c01c79`).
**Ở đâu:** `KeycloakAdmin.resources()` trả `{tên: _id}`.
**Liên quan:** resource_names (nhóm 3), collection.

### policy (Keycloak)
**Là gì:** một **điều kiện** trả PERMIT/DENY. Đây là khái niệm khác với "chính sách cache" (`Classification.policy`, nhóm 6).
**Ví dụ thật:** `p_any_user` (role customer hoặc employee), `p_region_north` (regex trên claim `region`).

### permission
**Là gì:** gắn một resource với các policy. `decisionStrategy=UNANIMOUS` nghĩa là mọi policy đều phải PERMIT.
**Ví dụ thật:** `read sales_north` = `p_sales` **và** `p_region_north`.

### decisionStrategy
**Là gì:** cách gộp kết quả nhiều policy: UNANIMOUS (tất cả), AFFIRMATIVE (ít nhất một), CONSENSUS (đa số).
**Ví dụ thật:** mọi permission ở đây dùng `UNANIMOUS`.

### fetchRoles
**Là gì:** tuỳ chọn của role policy: `true` thì Keycloak đọc role **hiện tại trong cơ sở dữ liệu**, không dựa vào role ghi trong token. Nhờ đó thu hồi role có hiệu lực ngay khi đánh giá.

### protocol mapper
**Là gì:** quy tắc đưa dữ liệu của user vào token.
**Ví dụ thật:** mapper `region` trên client `semcache-backend`: attribute `region` → claim `region`. Token của frontend **không** có claim này.

### evaluate (policy evaluate API)
**Là gì:** API của Keycloak trả lời "user này có được truy cập các resource này không", dựa trên dữ liệu hiện tại.
**Ví dụ thật:** `POST /admin/realms/semcache/clients/b241a711-…/authz/resource-server/policy/evaluate` với `{"userId": "...", "resources": [...]}`. Kết quả: `sales_bac → collection:sales_north: PERMIT`, `sales_nam → DENY`.
**Ở đâu:** `KeycloakAdmin.evaluate`.
**Liên quan:** resource_names, PERMIT/DENY.

### PERMIT / DENY
**Là gì:** kết quả đánh giá quyền của Keycloak; backend đổi thành `True` / `False`.

### admin event
**Là gì:** bản ghi Keycloak tạo ra mỗi khi có thay đổi qua Admin API. Backend đọc nó để biết quyền đã đổi.
**Ví dụ thật:** `{"time": 1794371861745, "operationType": "DELETE", "resourceType": "REALM_ROLE_MAPPING", "resourcePath": "users/829671b9-…/role-mappings/realm", "representation": "[{\"name\":\"cskh_agent\",…}]"}`. Keycloak 26.0 **không** có trường `id`.
**Ở đâu:** `KeycloakAdmin.admin_events`, `KeycloakEventSource.poll`, `_event_key`.
**Liên quan:** revocation window, AccessChangeEvent.

### token (access token, JWT)
**Là gì:** chuỗi đã ký số mà Keycloak cấp sau khi đăng nhập; frontend gửi kèm mỗi request (`Authorization: Bearer …`). Sống 15 phút.
**Ở đâu:** giải mã ở `auth.decode`.

### sub / preferred_username / azp / iss / realm_access (claims của token)
| Claim | Là gì | Ví dụ thật |
|---|---|---|
| `sub` | id user; backend dùng làm `user_id` | `829671b9-5f8b-431d-9b2f-8a31158a3a2d` (cskh1) |
| `preferred_username` | tên đăng nhập | `cskh1` |
| `azp` | client đã cấp token; backend chỉ nhận `semcache-frontend` | `semcache-frontend` |
| `iss` | nơi phát hành; phải khớp | `http://localhost:8080/realms/semcache` |
| `realm_access.roles` | role **tại lúc cấp token** (có thể cũ tới 15 phút) | `['employee','cskh_agent',…]` |
| `exp` / `iat` | hết hạn / phát hành (epoch) | `exp − iat = 900` |

### JWKS
**Là gì:** danh sách khoá công khai của Keycloak, dùng để kiểm tra chữ ký token.
**Ví dụ thật:** `http://localhost:8080/realms/semcache/protocol/openid-connect/certs`.
**Ở đâu:** `auth._jwks`.

### PKCE
**Là gì:** cơ chế bảo vệ quá trình đăng nhập cho ứng dụng chạy trên trình duyệt (public client).
**Ví dụ thật:** client frontend cấu hình `pkce.code.challenge.method = S256`.

---

## 3. Tham số & biến trong code

### `resource_names`
**Là gì:** danh sách **tên resource Keycloak** cần hỏi quyền, dạng `collection:<id>`. `None` nghĩa là **hỏi tất cả** resource (dùng khi tính signature).
**Ví dụ thật:** `None` (trong `/api/me` → tính signature); `['collection:cskh', 'collection:public']` (post-verify và reverify của cskh1); `['collection:cskh']` (audit).
**Ở đâu:** tham số của `KeycloakAdmin.evaluate(user_id, resource_names=None)` — `iam/keycloak.py`. Được tạo trong `KeycloakAccessControl.check_collections` bằng cách thêm tiền tố `collection:` vào tên collection.
**Liên quan:** resource, evaluate, collections.
*Thêm 11/11/2026 theo câu hỏi của bạn.*

### `user_id`
**Là gì:** id user trong Keycloak (= claim `sub`).
**Ví dụ thật:** `829671b9-5f8b-431d-9b2f-8a31158a3a2d` (cskh1).

### `user`
**Là gì:** đối tượng `UserContext` của người đang gọi, có sau bước xác thực; được truyền xuống hầu hết các hàm.

### `collections` / `cols`
**Là gì:** tập/danh sách **tên collection không có tiền tố** (khác `resource_names`).
**Ví dụ thật:** `['cskh','internal_all','public']` (signature của cskh1, dùng để lọc Qdrant); `{'cskh','public'}` (`cols` khi reverify).
**Ở đâu:** `Signature.collections`, `retrieval.search(vec, collections)`, `check_collections(user, collections)`.

### `namespaced`
**Là gì:** danh sách collection **có tiền tố namespace**, đầu vào để tính hash signature.
**Ví dụ thật:** `['keycloak:cskh','keycloak:internal_all','keycloak:public']`.
**Ở đâu:** `access.compute_hash(namespaced)`.

### `vec`
**Là gì:** vector embedding của câu hỏi (1536 số, đã chuẩn hoá).
**Ví dụ thật:** `[-0.0111, 0.0120, -0.0202, …]` cho "Khách VIP được đổi trả trong bao lâu?".

### `partition` (tham số)
**Là gì:** signature của người hỏi, truyền vào `cache.lookup` để chỉ tìm trong vùng của họ.
**Ví dụ thật:** `'95503c7831d2f7ed'`.

### `entities`
**Là gì:** dict entity của câu hỏi (xem entity, nhóm 1). Ví dụ: `{'tier': 'vip'}`.

### `prompt_version`
**Là gì:** mã phiên bản prompt `rag_answer`; đổi prompt thì mã đổi, entry cũ không được dùng lại.
**Ví dụ thật:** `'v1-8cc4d02d'` (= `v` + `version` trong prompts.yaml + 8 ký tự hash nội dung).
**Ở đâu:** `prompts.version`.

### `prompt_name` / `variables`
**Là gì:** tên prompt trong `prompts.yaml` và các biến điền vào prompt (`**variables`).
**Ví dụ thật:** `'rag_answer'`; `{question, context, history: '(không có)', no_answer: 'Tôi không tìm thấy…'}`.
**Ở đâu:** `llm.generate(prompt_name, **variables)`.

### `history`
**Là gì:** tối đa 4 tin nhắn gần nhất của session. **Chỉ đưa vào prompt khi câu hỏi là BYPASS** (câu nối tiếp).
**Ví dụ thật:** `[{role:'user', content:'Khách VIP…'}, {role:'assistant', content:'Khách hàng hạng VIP…'}]`.

### `label`
**Là gì:** nhãn ngắn của đoạn ngữ cảnh (`c1`…`c5`) để LLM trích dẫn.
**Ở đâu:** gán trong `retrieval.format_context`.

### `top_k` / `min_score`
**Là gì:** số đoạn tài liệu tối đa lấy ra (5) và điểm tối thiểu để giữ (0.25).
**Ở đâu:** `retrieval.search`; cấu hình `retrieval.*`.

### `tr`
**Là gì:** đối tượng `Trace` của request hiện tại, truyền vào `pipeline.answer` để mỗi bước ghi span.

### `since_ms` / `last_ms`
**Là gì:** mốc thời gian (mili-giây epoch) mà poller đọc admin event từ đó trở đi.
**Ví dụ thật:** đặt bằng thời điểm backend khởi động; tăng dần theo event mới nhất đã xử lý.
**Ở đâu:** `KeycloakEventSource`.

### `max_results`
**Là gì:** số admin event tối đa lấy mỗi lần poll (200). Xem WALKTHROUGH mục 13 điểm 6.

### `affects_all`
**Là gì:** cờ của `AccessChangeEvent`: thay đổi ảnh hưởng mọi user (vd sửa policy) → xoá mọi signature.

### `grant` / `actor`
**Là gì:** `grant=True` là cấp role, `False` là thu hồi. `actor` là admin thực hiện thao tác (ghi vào sự kiện).

---

## 4. Kiểu dữ liệu & trường
Chi tiết từng trường xem WALKTHROUGH mục 11. Tóm tắt:

| Kiểu | Một câu | Ví dụ thật |
|---|---|---|
| `UserContext` | người đang gọi (từ token) | `UserContext(user_id='829671b9-…', username='cskh1', roles=(…), display_name='Lan CSKH')` |
| `Signature` | kết quả tính signature | `Signature(signature='95503c7831d2f7ed', collections=[…], from_cache=True)` |
| `Classification` | kết quả phân loại câu hỏi | `Classification(policy='NORMAL', reason='câu hỏi tĩnh', intent='return_policy', intent_similarity=0.72, entities={'tier':'vip'})` |
| `Retrieved` | một đoạn tài liệu tìm được | `Retrieved(label='c2', chunk_id='9037da49391df36c', doc_id='vip_return_exception', score=0.7577, …)` |
| `LLMResult` | kết quả gọi Gemini | `LLMResult(text='…', tokens_in=725, tokens_out=44, latency_ms=3056, …)` |
| `CacheEntry` | một câu trả lời đã cache | xem cache entry (nhóm 1) |
| `Provenance` | một nguồn của câu trả lời | `Provenance(chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', …)` |
| `Candidate` | một entry ứng viên khi tra | xem candidate (nhóm 1) |
| `LookupResult` | kết quả tra cache | `LookupResult(hit=CacheEntry(…), similarity=0.8471, candidates=[…])` |
| `ChatResult` | kết quả pipeline trả cho endpoint | `ChatResult(trace_id='69867628-…', status='MISS', …)` |
| `AccessChangeEvent` | một thay đổi quyền đọc từ Keycloak | `AccessChangeEvent(kind='role_mapping', user_ids=['829671b9-…'], affects_all=False, …)` |
| `Chunk` | một đoạn sau khi cắt | xem chunk (nhóm 1) |
| `Trace` | bản ghi một request | xem trace (nhóm 1) |

### `UserContext.roles`
**Là gì:** role lấy **từ token** (có thể cũ tới 15 phút). Chỉ dùng để kiểm tra quyền vào Console; quyền đọc tài liệu luôn hỏi Keycloak. Xem WALKTHROUGH mục 13 điểm 9.

### `Signature.from_cache`
**Là gì:** `True` nếu lấy từ Redis, `False` nếu vừa hỏi Keycloak tính lại.

### `Candidate.reason`
**Là gì:** lý do một entry ứng viên bị loại hoặc được chọn. Đây là cột "Kết luận" trên Console. Các giá trị: xem WALKTHROUGH mục 5 (bảng "Điều kiện trượt").

### `Chunk.embed_text` / `section_path`
**Là gì:** `section_path` là đường dẫn tiêu đề (`Tiêu đề > Mục`). `embed_text = "[section_path]\n" + nội dung`, là văn bản thực sự đem đi embed.

### `CacheEntry.gen_tokens_in / gen_tokens_out / gen_cost_usd`
**Là gì:** chi phí đã bỏ ra để sinh câu trả lời lần đầu; mỗi lần HIT tính là **tiết kiệm** đúng bấy nhiêu.
**Ví dụ thật:** 725 + 44 = `saved_tokens 769` cho mỗi HIT của entry VIP.

---

## 5. Nơi lưu trữ (Redis, Qdrant, Postgres)

| Khoá / bảng | Loại | Chứa gì | Ví dụ thật |
|---|---|---|---|
| `sig:user:<user_id>` | Redis string, TTL 300 s | signature đang dùng của user | `{"signature":"95503c7831d2f7ed","collections":["cskh","internal_all","public"],"computed_at":…,"username":"cskh1"}` |
| `sig:known` | Redis hash | user_id → {username, signature} gần nhất (cho Console, bảng partition) | `{"829671b9-…": {"username":"cskh1","signature":"95503c…"}}` |
| `emb:<model>:<sha1(text)>` | Redis string, TTL 30 ngày | vector đã embed của một đoạn văn bản | `emb:text-embedding-3-small:a8e80ee4…` (26 khoá lúc này) |
| `cache:entry:<entry_id>` | Redis string, TTL = ttl entry | JSON CacheEntry | `cache:entry:13c22a20-…` |
| `cache:doc:<doc_id>` | Redis set | reverse index: entry dùng tài liệu này | `cache:doc:return_policy` |
| `cache:lru` | Redis sorted set | entry_id → lần dùng cuối (LRU) | |
| `cache:stats` | Redis hash | bộ đếm `invalidated_doc_update`, `evicted_lru` | rỗng sau khôi phục demo |
| `doc:version` | Redis hash | doc_id → version hiện tại | `{"return_policy":"1", …}` |
| `semcache:events` | Redis pub/sub | sự kiện realtime cho Console: `trace`, `audit`, `security` | |
| `chunks` | Qdrant collection | vector + payload đoạn tài liệu | payload `{chunk_id, doc_id, version, collection, title, section_path, text}` |
| `semantic_cache` | Qdrant collection | vector **câu hỏi** đã cache | payload `{entry_id, partition}` |
| `documents` | Postgres | danh sách tài liệu + version hiện tại | |
| `sessions`, `messages` | Postgres | lịch sử chat theo user | |
| `traces` | Postgres | mỗi request một dòng: status, token, chi phí, `spans`, `audit`, `unauthorized` | `status='HIT', partition='95503c…', similarity=0.847, saved_tokens=769` |
| `security_events` | Postgres | thay đổi quyền/tài liệu + mốc thời gian | `kind='doc_update', summary='return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry'` |

---

## 6. Trạng thái & nhãn

### Trạng thái của một câu trả lời (`status`)
| Giá trị | Nghĩa | Nhãn trên giao diện |
|---|---|---|
| `HIT` | trả từ cache | Từ cache |
| `MISS` | được phép cache nhưng không trúng → sinh mới (rồi có thể lưu) | Sinh mới |
| `NO_CACHE` | câu hỏi cá nhân, không được cache | Không cache |
| `BYPASS` | câu hỏi nối tiếp, bỏ qua cache | Không dùng cache |
| `ERROR` | lỗi khi xử lý | Lỗi |

### Chính sách cache của câu hỏi (`Classification.policy`)
| Giá trị | Khi nào | Hệ quả |
|---|---|---|
| `NORMAL` | câu hỏi tĩnh | tra + lưu cache, TTL 7 ngày |
| `SHORT_TTL` | có từ chỉ thời điểm ("tháng này", "năm nay"…) | tra + lưu, TTL 1 giờ |
| `NO_CACHE` | có từ cá nhân ("của tôi"…) | không tra, không lưu |
| `BYPASS` | câu nối tiếp ("thế còn…") hoặc dưới 4 từ | không tra, không lưu; history được đưa vào prompt |

### Tên span
`identity` (signature) → `embed` → `classify` → `cache_lookup` → [`cache_hit`] hoặc [`retrieval` → `iam_verify` → `llm` → `admission`]. Xem WALKTHROUGH mục 4.3.

### Loại sự kiện bảo mật (`security_events.kind`)
`permission_change` (đổi quyền, nguồn `keycloak`), `doc_update` (xuất bản tài liệu, nguồn `admin_api`).

### `AccessChangeEvent.kind`
`role_mapping` (đổi role/nhóm), `user_attribute` (sửa user), `policy` (sửa policy/resource → ảnh hưởng mọi user).

---

## 7. Cấu hình

### `configs/settings.yaml`
| Khoá | Ý nghĩa | Giá trị hiện tại |
|---|---|---|
| `cache.threshold_default` | ngưỡng similarity | 0.75 |
| `cache.threshold_by_intent` | ngưỡng riêng theo intent | `{}` |
| `cache.ttl_seconds.NORMAL / SHORT_TTL` | TTL entry | 604800 / 3600 |
| `cache.max_entries` | vượt thì LRU | 5000 |
| `cache.candidates` | số entry ứng viên mỗi lần tra | 3 |
| `cache.reverify_iam_on_hit` | bật điều kiện 6 | true |
| `access.signature_ttl_seconds` | TTL signature trong Redis | 300 |
| `access.event_poll_seconds` | chu kỳ đọc admin event | 2 |
| `access.signature_scheme_version` | tăng khi đổi cách tính signature | 1 |
| `retrieval.top_k / min_score` | số đoạn, điểm tối thiểu | 5 / 0.25 |
| `chunking.max_tokens / min_tokens / overlap_tokens` | kích thước chunk | 400 / 80 / 50 |
| `pricing.*` | USD / 1 triệu token, để ước lượng chi phí | 0.10 / 0.40 / 0.02 |

### `configs/classifier.yaml`
`policies` (từ khoá NO_CACHE / SHORT_TTL / BYPASS, `min_words`), `intent.examples` + `intent.min_similarity`, `entities` (từ điển entity).

### `configs/prompts.yaml`
`version` (một phần của prompt_version), `rag_answer` (system, user, temperature, max_output_tokens), `no_answer_text` (câu "không tìm thấy", không bao giờ được cache).

### `.env`
Key API (`OPENAI_API_KEY`, `GEMINI_API_KEY`), model (`LLM_MODEL`, `EMBEDDING_MODEL`), địa chỉ hạ tầng (`POSTGRES_*`, `QDRANT_URL`, `REDIS_URL`, `KEYCLOAK_URL`, `KEYCLOAK_PUBLIC_URL`), `KEYCLOAK_BACKEND_SECRET`. Chi tiết: [CONFIG.md](CONFIG.md).
