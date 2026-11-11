# Trạng thái dự án

Cập nhật: 10/11/2026. Kế hoạch gốc: `plan.md` (lưu ngoài repo). Dự án chia 4 giai đoạn:
**A. Luồng hoàn chỉnh trên dữ liệu pilot → B. Dữ liệu và bộ test đầy đủ → C. Đánh giá chi tiết (E1–E7) → D. Hoàn thiện, báo cáo.**

**Hiện tại: xong Giai đoạn A.** Giai đoạn B, C, D chưa làm.

---

## 1. Đã làm (Giai đoạn A)

### Hạ tầng
- [x] `docker-compose.yml`: Postgres 16, Keycloak 26.0.7, Qdrant 1.12, Redis 7.4. Profile `app` chạy thêm backend và frontend trong Docker.
- [x] `Makefile` cho mọi thao tác (`make help`).
- [x] `.env.example`. Key thật nằm trong `.env` (đã có trong `.gitignore`).

### Dữ liệu pilot (`data/pilot/`)
- [x] 10 tài liệu tiếng Việt thuộc 6 collection: `public`, `internal_all`, `cskh`, `hr_confidential`, `sales_north`, `sales_south`.
- [x] Chủ đề "đổi trả" được phân tầng theo quyền: public ghi 7 ngày, CSKH ghi VIP 33/47 ngày. Nhờ vậy kiểm tra rò rỉ mới có ý nghĩa.
- [x] `return_policy` có 2 version (7 ngày → 15 ngày) để thử invalidation.
- [x] `acl.yaml`: 6 role, 7 user, policy RBAC cộng ABAC theo thuộc tính `region` (regex policy).
- [x] `canaries.yaml`: các giá trị đặc trưng của tài liệu mật, dùng để audit rò rỉ.
- [x] `questions.yaml`: 9 câu hỏi gốc kèm paraphrase, hard negative (gói Bạc/Vàng), câu bypass.

### IAM (Keycloak)
- [x] `scripts/setup_keycloak.py` tự động tạo realm, role, client (frontend public PKCE, backend confidential), resource = collection, policy, permission, user. Xác nhận lại bằng cách đánh giá quyền từng user.
- [x] Adapter `KeycloakAccessControl`: `list_accessible_collections`, `check_collections`, dùng **service account có cache token**. PermRAG xin admin token mỗi lần check nên chậm. Mỗi lần đánh giá ở đây mất khoảng 40 ms.
- [x] Interface `AccessControlBase` / `ChangeEventSource` cùng stub GCP/AWS (chưa cài đặt) để mở rộng.
- [x] Lỗi IAM thì từ chối (fail-closed).

### Backend (`backend/app/`)
- [x] **Chunking theo cấu trúc Markdown** (mục, bảng, header path, không vượt ranh giới tài liệu, `chunk_id` có version).
- [x] **Ingest** vào Qdrant; registry version ở Postgres và Redis.
- [x] **Access signature** = hash(scheme_version, tập collection có namespace). Cache trong Redis có TTL.
- [x] **Retrieval lọc trước theo collection của signature**, sau đó **IAM kiểm tra lại** (post-verify).
- [x] **Gemini** trả lời có trích dẫn `[c1]`. Prompt nằm trong `configs/prompts.yaml`.
- [x] **Semantic cache:** partition theo signature, provenance, reverse index tài liệu → entry, LRU, TTL theo loại câu hỏi. Có 6 điều kiện hit: partition, similarity ≥ ngưỡng, entity khớp, version prompt, version tài liệu, TTL, cộng IAM re-verify. Mọi lý do trượt đều được ghi lại.
- [x] **Classifier dạng rule** (`configs/classifier.yaml`): NORMAL / SHORT_TTL / NO_CACHE (câu cá nhân) / BYPASS (câu nối tiếp). Intent xác định bằng embedding so với câu mẫu; entity bằng từ điển.
- [x] **Admission:** không cache câu "không tìm thấy", câu không có trích dẫn, câu không có ngữ cảnh.
- [x] **Đồng bộ quyền:** thread poll Keycloak admin-events mỗi 2 giây rồi xoá signature của user bị ảnh hưởng, ghi `security_events` (thời điểm xảy ra, phát hiện, có hiệu lực).
- [x] **Cập nhật tài liệu:** nạp version mới, xoá entry qua reverse index, ghi sự kiện.
- [x] **Tracing:** mỗi request là một trace gồm nhiều span, lưu Postgres, phát realtime qua Redis pub/sub → SSE.
- [x] **Audit canary chạy nền** sau mỗi câu trả lời: tìm canary rồi hỏi IAM xem user có quyền collection đó không. Nếu không có quyền thì tính là `unauthorized`.
- [x] Lịch sử chat theo session, **phân quyền theo chủ session**. Có feedback 👍/👎.
- [x] API Console (cần role `ops_admin`): metrics, traces, cache, security, admin (cấp/thu hồi role, xuất bản version, khôi phục dữ liệu demo).

### Frontend (`frontend/`)
- [x] Một app, một port, 2 route: `/chat` và `/console` (chỉ `ops_admin`). Code của Console được tách bundle riêng. User thường vào `/console` sẽ nhận trang 403.
- [x] Đăng nhập Keycloak (OIDC + PKCE).
- [x] **Chat:** sidebar session, gợi ý câu hỏi, trích dẫn, nhãn *Từ cache / Sinh mới / Không dùng cache*, độ trễ, 👍/👎.
- [x] **Console:**
  - **Tổng quan:** hit rate, token và chi phí tiết kiệm, số lượt vượt quyền, revocation window, biểu đồ theo phút, độ trễ p50/p95, bảng theo intent kèm gợi ý chỉnh ngưỡng.
  - **Request:** bảng cập nhật realtime, lọc theo trạng thái.
  - **Chi tiết request:** pipeline dạng timeline, gồm signature, phân loại, các ứng viên cache và lý do trượt, chunk retrieval, quyết định IAM, token, admission, audit.
  - **Cache:** entry, partition, xoá cache.
  - **Bảo mật:** dòng thời gian sự kiện và revocation window.
  - **Quản trị:** cấp/thu hồi role, xuất bản version tài liệu, khôi phục demo.
- [x] Giao diện liquid glass, có dark mode, fallback khi tắt hiệu ứng trong suốt hoặc giảm chuyển động.

### Test
- [x] `tests/test_units.py`: 14 unit test (chunking, classifier, entity, signature, prompt, canary, khử trùng event).
- [x] `scripts/smoke_api.py`: 8 bước luồng hoàn chỉnh qua API thật.
- [x] `frontend/e2e/flow.spec.ts`: **7 kịch bản Playwright** (plan mục 11.1). Pass cả khi chạy dev lẫn khi chạy toàn bộ trong Docker.

---

## 2. Chưa làm

### Giai đoạn B: dữ liệu và test đầy đủ
- [ ] Fact sheet (`data/world/facts.yaml`) và outline; sinh khoảng 200 tài liệu bằng Gemini, kiểm tra tự động, duyệt tay.
- [ ] Ngân hàng khoảng 150–300 câu hỏi gốc với paraphrase, hard negative, reference answer theo tổ hợp quyền.
- [ ] Workload generator (Zipf, drift, event timeline) và gán nhãn oracle.
- [ ] Đo fact recall@k để chốt cấu hình chunk (fixed-512 / structure-400 / structure-256).
- [ ] **Bộ test đầy đủ:** pytest tích hợp, test bảo mật canary trên toàn workload, mở rộng Playwright (nhiều session, tài liệu mới thêm, IAM lỗi thì fail-closed, đổi thuộc tính ABAC).

### Giai đoạn C: đánh giá chi tiết
- [ ] Baseline: không cache, exact-match, cache chung (naive), cache theo user, cache theo role.
- [ ] E1 calibrate ngưỡng (global và theo intent; so sánh small và large).
- [ ] E2 so sánh các chiến lược phân vùng.
- [ ] E3 revocation window theo chu kỳ poll, TTL, có/không re-verify.
- [ ] E4 eviction LRU/LFU/TTL/GDSF theo Zipf α và drift. **Hiện mới có LRU.**
- [ ] E5 có/không classifier. E6 lọc trước so với lọc sau. E7 timing side-channel. Ablation.
- [ ] **Semantic invalidation khi thêm tài liệu mới** (plan 4.6). Hiện chỉ dựa vào TTL.
- [ ] Kiểm chứng IAM mô hình khác (adapter giả lập ACL theo từng tài liệu, plan 4.4.1).

### Hướng mở rộng (không thuộc phạm vi chính)
- [ ] Viết lại câu nối tiếp thành câu độc lập bằng LLM. Hiện chỉ BYPASS.
- [ ] Adapter GCP/AWS thật. Mã hoá answer trong cache. Giảm timing side-channel. Cross-partition reuse.
- [ ] Streaming câu trả lời từng token. Hiện trả cả câu một lần.

---

## 3. Khác với plan và lý do
| Plan | Thực tế | Lý do |
|---|---|---|
| Ngưỡng similarity mặc định (chưa chốt) | 0.75, bỏ ngưỡng riêng theo intent | Đo trên pilot (xem mục 4); entity check xử lý hard negative tốt hơn tăng ngưỡng |
| Event bus Redis Streams | Poller trong backend xử lý trực tiếp, kết quả phát qua Redis pub/sub | Một tiến trình là đủ cho phạm vi pilot; interface `ChangeEventSource` vẫn tách riêng |
| Worker sync riêng | Thread nền trong backend | Đơn giản khi chạy; tách tiến trình khi cần scale |
| Streaming câu trả lời (12.2) | Chưa có | Ưu tiên luồng hoàn chỉnh; ghi vào phần mở rộng |

## 4. Phát hiện trong quá trình làm (dùng cho báo cáo)
1. **Embedding tiếng Việt cho similarity thấp hơn nhiều so với ngưỡng hay dùng.** Với `text-embedding-3-small`:
   - Paraphrase cùng câu hỏi: thấp nhất **0.57**, trung bình **0.77**, cao nhất 0.92. `-large`: thấp nhất 0.66, trung bình 0.83.
   - Hard negative "gói Bạc" vs "gói Vàng": **0.84**, cao hơn nhiều cặp paraphrase thật, nên **không có ngưỡng nào tách được**. Bắt buộc phải dùng entity check. Đây là số liệu chứng minh cho điều kiện 3 ở mục 4.5 của plan.
   - Ví dụ cặp "trả hàng trong mấy ngày" / "đổi trả sản phẩm trong bao nhiêu ngày": 0.713 < 0.75, nên bị MISS. Hit rate thực tế phụ thuộc mạnh vào ngưỡng, đúng là câu hỏi E1 cần trả lời.
2. **Keycloak 26.0 không trả `id` cho admin event.** Bản đầu khử trùng event theo `id`, nên chỉ nhận được event đầu tiên. Khi đó **lớp IAM re-verify vẫn chặn được** entry của partition cũ: request bị MISS và signature bị xoá. Đây là bằng chứng thực tế cho giá trị của defense-in-depth. Đã sửa bằng khoá ghép từ nội dung event.
3. Khi đồng bộ bằng event, revocation window đo được khoảng **0,3–1,9 giây** với chu kỳ poll 2 giây.
4. Độ trễ: HIT khoảng 25–50 ms (khi embedding câu hỏi đã có trong cache), MISS khoảng 1–3 giây (Gemini). Khớp với nhận định của paper PermRAG rằng LLM chiếm phần lớn thời gian.

## 5. Hạn chế đã biết
Xem thêm danh sách có bằng chứng ở [WALKTHROUGH.md mục 13](WALKTHROUGH.md#13-các-điểm-có-thể-chưa-hợp-lý).

- Similarity dùng cosine trên câu hỏi gốc, chưa chuẩn hoá tiếng Việt (bỏ dấu, từ đồng nghĩa).
- Audit canary chỉ phát hiện rò rỉ **có canary**. Thông tin mật diễn đạt lại bằng chữ thì không bắt được (Giai đoạn C sẽ dùng thêm LLM-judge trên mẫu).
- Pilot nhỏ (10 tài liệu, 24 chunk). Số liệu ở mục 4 chỉ mang tính định hướng.
- Token Keycloak của frontend sống 15 phút. Vai trò hiển thị trong token có thể cũ, nhưng **quyết định quyền luôn lấy từ IAM**, không lấy từ token.
