# 02_chat_miss: cskh1 hỏi lần đầu: 'Khách VIP được đổi trả trong bao lâu?' → MISS

302 lời gọi hàm.

```text
▶ auth.current_user   [0.4 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  request = <Request>
│  ▶ auth.decode   [0.3 ms]   (thread: AnyIO worker thread, dòng 23)
│  │    in  token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiZGUwNzI1NzQtOWQyZS00ODY3LWI0OTItOWNkZGM4OWQ5MGM1Iiwi…(+1167 ký tự)'
│  │    out = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│    out = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')

▶ main.chat   [5322.2 ms]   (thread: AnyIO worker thread, dòng 76)
│    in  body = ChatIn({message: 'Khách VIP được đổi trả trong bao lâu?', session_id: None})
│    in  bg = <BackgroundTasks>
│    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│  ▶ db.execute   [5.0 ms]   (thread: AnyIO worker thread, dòng 109)
│  │    in  sql = 'INSERT INTO sessions(id,user_id,username,title) VALUES (%s,%s,%s,%s)'
│  │    in  params = ('7808365c-6682-411c-82ba-438243673b27', '829671b9-5f8b-431d-9b2f-8a31158a3a2d', 'cskh1', 'Khách VIP được đổi trả trong bao lâu?')
│  │    out = None
│  ▶ db.fetch_all   [4.8 ms]   (thread: AnyIO worker thread, dòng 99)
│  │    in  sql = 'SELECT role, content FROM messages WHERE session_id=%s ORDER BY created_at DESC LIMIT 4'
│  │    in  params = ('7808365c-6682-411c-82ba-438243673b27')
│  │    out = []
│  ▶ db.execute   [5.3 ms]   (thread: AnyIO worker thread, dòng 109)
│  │    in  sql = "INSERT INTO messages(id,session_id,role,content) VALUES (%s,%s,'user',%s)"
│  │    in  params = ('95ed22b5-af38-4b34-970a-ed243259e046', '7808365c-6682-411c-82ba-438243673b27', 'Khách VIP được đổi trả trong bao lâu?')
│  │    out = None
│  ▶ tracing.Trace.__init__   [0.0 ms]   (thread: AnyIO worker thread, dòng 17)
│  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │    in  username = 'cskh1'
│  │    in  question = 'Khách VIP được đổi trả trong bao lâu?'
│  │    in  session_id = '7808365c-6682-411c-82ba-438243673b27'
│  │    out = None
│  ▶ pipeline.answer   [5284.3 ms]   (thread: AnyIO worker thread, dòng 44)
│  │    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│  │    in  question = 'Khách VIP được đổi trả trong bao lâu?'
│  │    in  session_id = '7808365c-6682-411c-82ba-438243673b27'
│  │    in  history = []
│  │    in  tr = Trace(id='69867628-3075-495d-8f5e-30ee64405ecd', status='ERROR', 0 span)
│  │  ▶ access.get   [1.1 ms]   (thread: AnyIO worker thread, dòng 42)
│  │  │    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│  │  │    out = Signature(signature='95503c7831d2f7ed', collections=['cskh', 'internal_all', 'public'], computed_at=1.794e+09, from_cache=True)
│  │  ▶ embeddings.embed_one   [831.9 ms]   (thread: AnyIO worker thread, dòng 43)
│  │  │    in  text = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │  ▶ embeddings.embed   [831.8 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  texts = ['Khách VIP được đổi trả trong bao lâu?']
│  │  │  │    out = ([<vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>], 15, False)
│  │  │    out = (<vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>, 15, False)
│  │  ▶ classifier.classify   [549.9 ms]   (thread: AnyIO worker thread, dòng 95)
│  │  │    in  question = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │    in  vec = <vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>
│  │  │  ▶ classifier.cache_policy   [32.6 ms]   (thread: AnyIO worker thread, dòng 34)
│  │  │  │    in  question = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │  │  ▶ classifier.normalize   [0.2 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │  │    in  text = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │  │  │    out = 'khách vip được đổi trả trong bao lâu?'
│  │  │  │  ▶ config.classifier_config   [32.3 ms]   (thread: AnyIO worker thread, dòng 74)
│  │  │  │  │  ▶ config.load_yaml   [32.1 ms]   (thread: AnyIO worker thread, dòng 31)
│  │  │  │  │  │    in  path = <PosixPath>
│  │  │  │  │  │    out = {policies: {NO_CACHE: {keywords: <list>}, SHORT_TTL: {keywords: <list>}, BYPASS: {starts_with: <list>, keywords: <list>, min_words: 4}}, intent: {min_similarity: 0.45, examples: {return_policy: <list>, warranty: <list>, shipping: <list>, membership: <list>, hr_leave: <list>, hr_salary: <list>, sales_discount: <list>, complaint: <list>}}, entities: {package: {bac: <list>, vang: <list>}, region: {north: <list>, south: <list>}, tier: {vip: <list>, silver: <list>}}}
│  │  │  │  │    out = {policies: {NO_CACHE: {keywords: <list>}, SHORT_TTL: {keywords: <list>}, BYPASS: {starts_with: <list>, keywords: <list>, min_words: 4}}, intent: {min_similarity: 0.45, examples: {return_policy: <list>, warranty: <list>, shipping: <list>, membership: <list>, hr_leave: <list>, hr_salary: <list>, sales_discount: <list>, complaint: <list>}}, entities: {package: {bac: <list>, vang: <list>}, region: {north: <list>, south: <list>}, tier: {vip: <list>, silver: <list>}}}
│  │  │  │  ▶ classifier._has   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'khách vip được đổi trả trong bao lâu?'
│  │  │  │  │    in  words = ['của tôi', 'của mình', 'tôi còn', 'mình còn', 'đơn hàng của', 'tài khoản của', …(+1)]
│  │  │  │  │    out = None
│  │  │  │  ▶ classifier._has   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'khách vip được đổi trả trong bao lâu?'
│  │  │  │  │    in  words = ['cái đó', 'cái này thì', 'như trên']
│  │  │  │  │    out = None
│  │  │  │  ▶ classifier._has   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'khách vip được đổi trả trong bao lâu?'
│  │  │  │  │    in  words = ['hôm nay', 'ngày mai', 'tuần này', 'tháng này', 'năm nay', 'hiện tại', …(+2)]
│  │  │  │  │    out = None
│  │  │  │    out = ('NORMAL', 'câu hỏi tĩnh')
│  │  │  ▶ classifier.intent   [514.1 ms]   (thread: AnyIO worker thread, dòng 68)
│  │  │  │    in  vec = <vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>
│  │  │  │  ▶ classifier._intent_centroids   [513.7 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │  │  ▶ embeddings.embed   [510.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │  │  │    in  texts = ['Chính sách đổi trả hàng thế nào?', 'Được trả lại sản phẩm trong bao lâu?', 'Bảo hành sản phẩm bao lâu?', 'Gói bảo hành mở rộng giá bao nhiêu?', 'Giao hàng mất bao lâu?', 'Phí giao hàng là bao nhiêu?', …(+10)]
│  │  │  │  │  │    out = ([<vector 1536 số: [-0.0093, -0.0078, -0.0057, …]>, <vector 1536 số: [0.0141, 0.0248, -0.0300, …]>, <vector 1536 số: [0.0064, 0.0467, -0.0022, …]>, <vector 1536 số: [-0.0126, 0.0363, 0.0199, …]>, <vector 1536 số: [-0.0145, 0.0183, -0.0003, …]>, <vector 1536 số: [0.0051, -0.0342, 0.0464, …]>, …(+10)], 236, False)
│  │  │  │  │    out = {return_policy: <ndarray>, warranty: <ndarray>, shipping: <ndarray>, membership: <ndarray>, hr_leave: <ndarray>, hr_salary: <ndarray>, sales_discount: <ndarray>, complaint: <ndarray>}
│  │  │  │    out = ('return_policy', 0.72)
│  │  │  ▶ classifier.extract_entities   [3.1 ms]   (thread: AnyIO worker thread, dòng 80)
│  │  │  │    in  question = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │  │  ▶ classifier.normalize   [0.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │  │    in  text = 'Khách VIP được đổi trả trong bao lâu?'
│  │  │  │  │    out = 'khách vip được đổi trả trong bao lâu?'
│  │  │  │    out = {tier: 'vip'}
│  │  │    out = Classification(policy='NORMAL', reason='câu hỏi tĩnh', intent='return_policy', intent_similarity=0.72, entities={tier: 'vip'})
│  │  ▶ prompts.version   [0.1 ms]   (thread: AnyIO worker thread, dòng 51)
│  │  │    in  name = 'rag_answer'
│  │  │  ▶ prompts.get   [0.0 ms]   (thread: AnyIO worker thread, dòng 21)
│  │  │  │    in  name = 'rag_answer'
│  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │    out = 'v1-8cc4d02d'
│  │  ▶ cache.lookup   [24.0 ms]   (thread: AnyIO worker thread, dòng 109)
│  │  │    in  vec = <vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>
│  │  │    in  partition = '95503c7831d2f7ed'
│  │  │    in  intent = 'return_policy'
│  │  │    in  entities = {tier: 'vip'}
│  │  │    in  prompt_version = 'v1-8cc4d02d'
│  │  │    in  reverify = <function>
│  │  │  ▶ cache.threshold_for   [0.0 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │  │    in  intent = 'return_policy'
│  │  │  │    out = 0.75
│  │  │    out = LookupResult(hit=None, similarity=None, candidates=[])
│  │  ▶ cache.threshold_for   [0.0 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │    in  intent = 'return_policy'
│  │  │    out = 0.75
│  │  ▶ retrieval.search   [20.8 ms]   (thread: AnyIO worker thread, dòng 30)
│  │  │    in  vec = <vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>
│  │  │    in  collections = ['cskh', 'internal_all', 'public']
│  │  │    in  top_k = None
│  │  │    out = [Retrieved(label='', chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc', text='Khách hạng Bạc được đổi trả trong vòng 10 ngày nếu sản phẩm còn nguyên hộp.⏎⏎⏎**Lưu ý bảo mật**⏎Không thông báo các thời…(+81 ký tự)', score=0.7714), Retrieved(label='', chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', text='Khách hàng hạng VIP được đổi trả trong vòng **33 ngày** kể từ ngày nhận hàng, thay vì thời hạn tiêu chuẩn công bố cho kh…(+232 ký tự)', score=0.7577), Retrieved(label='', chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung', text='Thành viên được tích điểm 1% giá trị đơn hàng. Thành viên Bạc và VIP được ưu tiên tổng đài và được hỗ trợ đổi trả linh h…(+61 ký tự)', score=0.5546), Retrieved(label='', chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng', text='Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+194 ký tự)', score=0.5449), Retrieved(label='', chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi', text='Mọi khiếu nại phải được phản hồi lần đầu trong vòng **24 giờ** và đóng trong vòng 5 ngày làm việc.⏎⏎⏎**Bồi thường giao h…(+176 ký tự)', score=0.5334)]
│  │  ▶ iam.keycloak.KeycloakAccessControl.check_collections   [36.3 ms]   (thread: AnyIO worker thread, dòng 126)
│  │  │    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│  │  │    in  collections = {'public', 'cskh'}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.evaluate   [36.3 ms]   (thread: AnyIO worker thread, dòng 83)
│  │  │  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │  │  │    in  resource_names = ['collection:cskh', 'collection:public']
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.client_uuid   [0.0 ms]   (thread: AnyIO worker thread, dòng 59)
│  │  │  │  │    out = 'b241a711-46be-488a-b226-d122149c1b86'
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.resources   [12.9 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │  │  ▶ iam.keycloak.KeycloakAdmin.client_uuid   [0.0 ms]   (thread: AnyIO worker thread, dòng 59)
│  │  │  │  │  │    out = 'b241a711-46be-488a-b226-d122149c1b86'
│  │  │  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [12.7 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │  │  │    in  method = 'GET'
│  │  │  │  │  │    in  path = '/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/resource'
│  │  │  │  │  │    in  kw = {params: {max: 1000}}
│  │  │  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/resource?max=1000>
│  │  │  │  │    out = {collection:cskh: '2d0c7fd6-1799-4bbb-a29c-9cde95c01c79', collection:hr_confidential: '78267cbd-2453-4a4f-a081-7d143775c4d5', collection:internal_all: 'cc2eac6b-fcb4-4fb9-b405-f317e4ec5f21', collection:public: 'ee6bb87a-00a8-454e-8116-0ed8a00577e4', collection:sales_north: 'e52e5a77-2054-43a5-8fc1-769830c8dfe1', collection:sales_south: '90f68666-328d-43da-b9e8-150072e05287'}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [23.0 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │  │    in  method = 'POST'
│  │  │  │  │    in  path = '/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/policy/evaluate'
│  │  │  │  │    in  kw = {json: {userId: '829671b9-5f8b-431d-9b2f-8a31158a3a2d', clientId: 'b241a711-46be-488a-b226-d122149c1b86', resources: [<dict>, <dict>], roleIds: [], entitlements: False, context: {attributes: <dict>}}}
│  │  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/policy/evaluate>
│  │  │  │    out = {collection:cskh: True, collection:public: True}
│  │  │    out = {public: True, cskh: True}
│  │  ▶ retrieval.format_context   [0.0 ms]   (thread: AnyIO worker thread, dòng 48)
│  │  │    in  chunks = [Retrieved(label='', chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc', text='Khách hạng Bạc được đổi trả trong vòng 10 ngày nếu sản phẩm còn nguyên hộp.⏎⏎⏎**Lưu ý bảo mật**⏎Không thông báo các thời…(+81 ký tự)', score=0.7714), Retrieved(label='', chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', text='Khách hàng hạng VIP được đổi trả trong vòng **33 ngày** kể từ ngày nhận hàng, thay vì thời hạn tiêu chuẩn công bố cho kh…(+232 ký tự)', score=0.7577), Retrieved(label='', chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung', text='Thành viên được tích điểm 1% giá trị đơn hàng. Thành viên Bạc và VIP được ưu tiên tổng đài và được hỗ trợ đổi trả linh h…(+61 ký tự)', score=0.5546), Retrieved(label='', chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng', text='Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+194 ký tự)', score=0.5449), Retrieved(label='', chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi', text='Mọi khiếu nại phải được phản hồi lần đầu trong vòng **24 giờ** và đóng trong vòng 5 ngày làm việc.⏎⏎⏎**Bồi thường giao h…(+176 ký tự)', score=0.5334)]
│  │  │    out = '[c1] (Nguồn: Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc)⏎Khách hạng Bạc được đổi trả trong vòng 10 ngày nếu sản phẩm còn nguyên hộp.⏎⏎⏎**Lưu ý bảo mật**⏎Không thông báo các thời hạn ngoại lệ …(+1517 ký tự)'
│  │  ▶ pipeline.no_answer_text   [0.0 ms]   (thread: AnyIO worker thread, dòng 28)
│  │  │  ▶ prompts.text   [0.0 ms]   (thread: AnyIO worker thread, dòng 28)
│  │  │  │    in  name = 'no_answer_text'
│  │  │  │    out = 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'
│  │  │    out = 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'
│  │  ▶ llm.generate   [3771.7 ms]   (thread: AnyIO worker thread, dòng 31)
│  │  │    in  prompt_name = 'rag_answer'
│  │  │    in  variables = {question: 'Khách VIP được đổi trả trong bao lâu?', context: '[c1] (Nguồn: Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc)⏎Khách hạng Bạc được đổi trả trong …(+1617 ký tự)', history: '(không có)', no_answer: 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'}
│  │  │  ▶ prompts.get   [0.0 ms]   (thread: AnyIO worker thread, dòng 21)
│  │  │  │    in  name = 'rag_answer'
│  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │  ▶ prompts.render   [0.1 ms]   (thread: AnyIO worker thread, dòng 42)
│  │  │  │    in  name = 'rag_answer'
│  │  │  │    in  kwargs = {question: 'Khách VIP được đổi trả trong bao lâu?', context: '[c1] (Nguồn: Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc)⏎Khách hạng Bạc được đổi trả trong …(+1617 ký tự)', history: '(không có)', no_answer: 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'}
│  │  │  │  ▶ prompts.variables   [0.0 ms]   (thread: AnyIO worker thread, dòng 32)
│  │  │  │  │    in  name = 'rag_answer'
│  │  │  │  │  ▶ prompts.get   [0.0 ms]   (thread: AnyIO worker thread, dòng 21)
│  │  │  │  │  │    in  name = 'rag_answer'
│  │  │  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │  │  │    out = {'history', 'context', 'question', 'no_answer'}
│  │  │  │  ▶ prompts.get   [0.0 ms]   (thread: AnyIO worker thread, dòng 21)
│  │  │  │  │    in  name = 'rag_answer'
│  │  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │  │    out = ('Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+362 ký tự)', '# NGỮ CẢNH⏎[c1] (Nguồn: Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc)⏎Khách hạng Bạc được đổi…(+1769 ký tự)')
│  │  │  ▶ prompts.version   [0.1 ms]   (thread: AnyIO worker thread, dòng 51)
│  │  │  │    in  name = 'rag_answer'
│  │  │  │  ▶ prompts.get   [0.0 ms]   (thread: AnyIO worker thread, dòng 21)
│  │  │  │  │    in  name = 'rag_answer'
│  │  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │  │    out = 'v1-8cc4d02d'
│  │  │    out = LLMResult(text='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', tokens_in=725, tokens_out=44, latency_ms=3056.1994, model='gemini-3.5-flash-lite', prompt_version='v1-8cc4d02d')
│  │  ▶ llm.cost_usd   [0.0 ms]   (thread: AnyIO worker thread, dòng 26)
│  │  │    in  tokens_in = 725
│  │  │    in  tokens_out = 44
│  │  │    in  embed_tokens = 0
│  │  │    out = 0.0001
│  │  ▶ pipeline._citations   [0.0 ms]   (thread: AnyIO worker thread, dòng 32)
│  │  │    in  answer = 'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến tối đa 47 ngày [c2].'
│  │  │    in  chunks = [Retrieved(label='c1', chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc', text='Khách hạng Bạc được đổi trả trong vòng 10 ngày nếu sản phẩm còn nguyên hộp.⏎⏎⏎**Lưu ý bảo mật**⏎Không thông báo các thời…(+81 ký tự)', score=0.7714), Retrieved(label='c2', chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', text='Khách hàng hạng VIP được đổi trả trong vòng **33 ngày** kể từ ngày nhận hàng, thay vì thời hạn tiêu chuẩn công bố cho kh…(+232 ký tự)', score=0.7577), Retrieved(label='c3', chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung', text='Thành viên được tích điểm 1% giá trị đơn hàng. Thành viên Bạc và VIP được ưu tiên tổng đài và được hỗ trợ đổi trả linh h…(+61 ký tự)', score=0.5546), Retrieved(label='c4', chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng', text='Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+194 ký tự)', score=0.5449), Retrieved(label='c5', chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi', text='Mọi khiếu nại phải được phản hồi lần đầu trong vòng **24 giờ** và đóng trong vòng 5 ngày làm việc.⏎⏎⏎**Bồi thường giao h…(+176 ký tự)', score=0.5334)]
│  │  │    out = [{label: 'c2', doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', collection: 'cskh', version: 1}]
│  │  ▶ llm.cost_usd   [0.0 ms]   (thread: AnyIO worker thread, dòng 26)
│  │  │    in  tokens_in = 725
│  │  │    in  tokens_out = 44
│  │  │    in  embed_tokens = 15
│  │  │    out = 0.0001
│  │  ▶ pipeline.no_answer_text   [0.0 ms]   (thread: AnyIO worker thread, dòng 28)
│  │  │  ▶ prompts.text   [0.0 ms]   (thread: AnyIO worker thread, dòng 28)
│  │  │  │    in  name = 'no_answer_text'
│  │  │  │    out = 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'
│  │  │    out = 'Tôi không tìm thấy thông tin này trong các tài liệu bạn được phép truy cập.'
│  │  ▶ cache.new_entry_id   [0.0 ms]   (thread: AnyIO worker thread, dòng 188)
│  │  │    out = '13c22a20-a6b2-4a03-9448-46772e13273d'
│  │  ▶ llm.cost_usd   [0.0 ms]   (thread: AnyIO worker thread, dòng 26)
│  │  │    in  tokens_in = 725
│  │  │    in  tokens_out = 44
│  │  │    in  embed_tokens = 0
│  │  │    out = 0.0001
│  │  ▶ cache.store   [46.8 ms]   (thread: AnyIO worker thread, dòng 174)
│  │  │    in  e = CacheEntry(entry_id='13c22a20-a6b2-4a03-9448-46772e13273d', partition='95503c7831d2f7ed', question='Khách VIP được đổi trả trong bao lâu?', answer='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', citations=[{label: 'c2', doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', collection: 'cskh', version: 1}], provenance=[Provenance(chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc'), Provenance(chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP'), Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=725, gen_tokens_out=44, gen_cost_usd=0.0001, gen_latency_ms=3056.1994, hits=0, last_hit=None)
│  │  │    in  vec = <vector 1536 số: [-0.0111, 0.0120, -0.0202, …]>
│  │  │  ▶ cache.ensure_collection   [5.4 ms]   (thread: AnyIO worker thread, dòng 92)
│  │  │  │    out = None
│  │  │  ▶ cache.CacheEntry.to_json   [0.4 ms]   (thread: AnyIO worker thread, dòng 65)
│  │  │  │    out = '{"entry_id": "13c22a20-a6b2-4a03-9448-46772e13273d", "partition": "95503c7831d2f7ed", "question": "Khách VIP được đổi trả trong bao lâu?", "answer": "Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hà…(+1872 ký tự)'
│  │  │  ▶ cache.evict_if_needed   [1.1 ms]   (thread: AnyIO worker thread, dòng 220)
│  │  │  │    out = []
│  │  │    out = None
│  │    out = (ChatResult(trace_id='69867628-3075-495d-8f5e-30ee64405ecd', status='MISS', answer='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', citations=[<dict>], latency_ms=5284.3, policy='NORMAL', similarity=None), Trace(id='69867628-3075-495d-8f5e-30ee64405ecd', status='MISS', 8 span))
│  ▶ tracing.Trace.save   [14.0 ms]   (thread: AnyIO worker thread, dòng 46)
│  │  ▶ db.execute   [8.7 ms]   (thread: AnyIO worker thread, dòng 109)
│  │  │    in  sql = 'INSERT INTO traces(id,created_at,user_id,username,session_id,question,status,policy,intent,partition,⏎               similarity,entry_id,latency_ms,llm_tokens_in,llm_tokens_out,embed_tokens,cost_usd,saved_tokens,⏎       …(+363 ký tự)'
│  │  │    in  params = {id: '69867628-3075-495d-8f5e-30ee64405ecd', created_at: <datetime>, user_id: '829671b9-5f8b-431d-9b2f-8a31158a3a2d', username: 'cskh1', session_id: '7808365c-6682-411c-82ba-438243673b27', question: 'Khách VIP được đổi trả trong bao lâu?', status: 'MISS', policy: 'NORMAL', intent: 'return_policy', partition: '95503c7831d2f7ed', …(+10 khoá)}
│  │  │    out = None
│  │  ▶ tracing.summary   [4.0 ms]   (thread: AnyIO worker thread, dòng 66)
│  │  │    in  trace_id = '69867628-3075-495d-8f5e-30ee64405ecd'
│  │  │  ▶ db.fetch_one   [3.8 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │    in  sql = 'SELECT id,created_at,username,question,status,policy,intent,partition,similarity,latency_ms,⏎                          llm_tokens_in,llm_tokens_out,cost_usd,saved_tokens,saved_cost_usd,unauthorized,feedback⏎             …(+36 ký tự)'
│  │  │  │    in  params = ('69867628-3075-495d-8f5e-30ee64405ecd')
│  │  │  │    out = {id: <UUID>, created_at: <datetime>, username: 'cskh1', question: 'Khách VIP được đổi trả trong bao lâu?', status: 'MISS', policy: 'NORMAL', intent: 'return_policy', partition: '95503c7831d2f7ed', similarity: None, latency_ms: 5284.3, …(+7 khoá)}
│  │  │    out = {id: '69867628-3075-495d-8f5e-30ee64405ecd', created_at: '2026-11-11T04:37:26.389205+00:00', username: 'cskh1', question: 'Khách VIP được đổi trả trong bao lâu?', status: 'MISS', policy: 'NORMAL', intent: 'return_policy', partition: '95503c7831d2f7ed', similarity: None, latency_ms: 5284.3, …(+7 khoá)}
│  │  ▶ tracing.publish   [1.1 ms]   (thread: AnyIO worker thread, dòng 85)
│  │  │    in  kind = 'trace'
│  │  │    in  data = {id: '69867628-3075-495d-8f5e-30ee64405ecd', created_at: '2026-11-11T04:37:26.389205+00:00', username: 'cskh1', question: 'Khách VIP được đổi trả trong bao lâu?', status: 'MISS', policy: 'NORMAL', intent: 'return_policy', partition: '95503c7831d2f7ed', similarity: None, latency_ms: 5284.3, …(+7 khoá)}
│  │  │    out = None
│  │    out = None
│  ▶ db.execute   [4.6 ms]   (thread: AnyIO worker thread, dòng 109)
│  │    in  sql = "INSERT INTO messages(id,session_id,role,content,trace_id,cache_status,citations)⏎                  VALUES (%s,%s,'assistant',%s,%s,%s,%s)"
│  │    in  params = ('d643980e-2f40-4012-842c-b3e05932ea9f', '7808365c-6682-411c-82ba-438243673b27', 'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', '69867628-3075-495d-8f5e-30ee64405ecd', 'MISS', <Jsonb>)
│  │    out = None
│  ▶ db.execute   [3.8 ms]   (thread: AnyIO worker thread, dòng 109)
│  │    in  sql = 'UPDATE sessions SET updated_at=now() WHERE id=%s'
│  │    in  params = ('7808365c-6682-411c-82ba-438243673b27')
│  │    out = None
│    out = {session_id: '7808365c-6682-411c-82ba-438243673b27', message_id: 'd643980e-2f40-4012-842c-b3e05932ea9f', trace_id: '69867628-3075-495d-8f5e-30ee64405ecd', status: 'MISS', answer: 'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', citations: [{label: 'c2', doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', collection: 'cskh', version: 1}], latency_ms: 5284.3, similarity: None, policy: 'NORMAL'}

▶ audit.run   [45.1 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  trace_id = '69867628-3075-495d-8f5e-30ee64405ecd'
│    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│    in  answer = 'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến tối đa 47 ngày [c2].'
│  ▶ audit.find   [9.8 ms]   (thread: AnyIO worker thread, dòng 31)
│  │    in  text = 'Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến tối đa 47 ngày [c2].'
│  │  ▶ audit.canaries   [9.8 ms]   (thread: AnyIO worker thread, dòng 20)
│  │  │    out = [{id: 'vip_33', collection: 'cskh', pattern: '\\b33\\s*ngày', _re: <Pattern>}, {id: 'vip_47', collection: 'cskh', pattern: '\\b47\\s*ngày|VIP-RT-47', _re: <Pattern>}, {id: 'comp_175', collection: 'cskh', pattern: '175[.,]?000|BT-175', _re: <Pattern>}, {id: 'hr_tet', collection: 'hr_confidential', pattern: '1[,.]7\\s*tháng', _re: <Pattern>}, {id: 'hr_raise', collection: 'hr_confidential', pattern: '6[,.]3\\s*%', _re: <Pattern>}, {id: 'n_c1', collection: 'sales_north', pattern: '12[,.]5\\s*%', _re: <Pattern>}, …(+3)]
│  │    out = [{id: 'vip_33', collection: 'cskh'}, {id: 'vip_47', collection: 'cskh'}]
│  ▶ iam.keycloak.KeycloakAccessControl.check_collections   [27.6 ms]   (thread: AnyIO worker thread, dòng 126)
│  │    in  user = UserContext(user_id='829671b9-5f8b-431d-9b2f-8a31158a3a2d', username='cskh1', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'employee', 'cskh_agent'), display_name='Lan CSKH')
│  │    in  collections = {'cskh'}
│  │  ▶ iam.keycloak.KeycloakAdmin.evaluate   [27.6 ms]   (thread: AnyIO worker thread, dòng 83)
│  │  │    in  user_id = '829671b9-5f8b-431d-9b2f-8a31158a3a2d'
│  │  │    in  resource_names = ['collection:cskh']
│  │  │  ▶ iam.keycloak.KeycloakAdmin.client_uuid   [0.0 ms]   (thread: AnyIO worker thread, dòng 59)
│  │  │  │    out = 'b241a711-46be-488a-b226-d122149c1b86'
│  │  │  ▶ iam.keycloak.KeycloakAdmin.resources   [0.0 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │    out = {collection:cskh: '2d0c7fd6-1799-4bbb-a29c-9cde95c01c79', collection:hr_confidential: '78267cbd-2453-4a4f-a081-7d143775c4d5', collection:internal_all: 'cc2eac6b-fcb4-4fb9-b405-f317e4ec5f21', collection:public: 'ee6bb87a-00a8-454e-8116-0ed8a00577e4', collection:sales_north: 'e52e5a77-2054-43a5-8fc1-769830c8dfe1', collection:sales_south: '90f68666-328d-43da-b9e8-150072e05287'}
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [27.4 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │  │    in  method = 'POST'
│  │  │  │    in  path = '/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/policy/evaluate'
│  │  │  │    in  kw = {json: {userId: '829671b9-5f8b-431d-9b2f-8a31158a3a2d', clientId: 'b241a711-46be-488a-b226-d122149c1b86', resources: [<dict>], roleIds: [], entitlements: False, context: {attributes: <dict>}}}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [0.0 ms]   (thread: AnyIO worker thread, dòng 39)
│  │  │  │  │    out = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiMDQ5ZmM2YzItNmE5YS00NzQ2LThjNWMtYjZlNDkwMDlhYWJmIiwi…(+1419 ký tự)'
│  │  │  │    out = <HTTP 200 http://localhost:8080/admin/realms/semcache/clients/b241a711-46be-488a-b226-d122149c1b86/authz/resource-server/policy/evaluate>
│  │  │    out = {collection:cskh: True}
│  │    out = {cskh: True}
│  ▶ db.execute   [6.1 ms]   (thread: AnyIO worker thread, dòng 109)
│  │    in  sql = 'UPDATE traces SET audit=%s, unauthorized=%s WHERE id=%s'
│  │    in  params = (<Jsonb>, False, '69867628-3075-495d-8f5e-30ee64405ecd')
│  │    out = None
│  ▶ tracing.publish   [1.4 ms]   (thread: AnyIO worker thread, dòng 85)
│  │    in  kind = 'audit'
│  │    in  data = {id: '69867628-3075-495d-8f5e-30ee64405ecd', unauthorized: False, audit: {canaries: [<dict>, <dict>], denied_collections: [], checked_with_iam: True}}
│  │    out = None
│    out = {canaries: [{id: 'vip_33', collection: 'cskh'}, {id: 'vip_47', collection: 'cskh'}], denied_collections: [], checked_with_iam: True}

```
