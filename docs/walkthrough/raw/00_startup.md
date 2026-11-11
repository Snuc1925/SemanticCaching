# 00_startup: Khởi động / import

97 lời gọi hàm.

```text
▶ config.Env   [0.0 ms]   (thread: MainThread, dòng 36)
│    out = None

▶ iam.base.UserContext   [0.0 ms]   (thread: MainThread, dòng 14)
│    out = None

▶ iam.base.AccessChangeEvent   [0.0 ms]   (thread: MainThread, dòng 22)
│    out = None

▶ iam.base.AccessControlBase   [0.0 ms]   (thread: MainThread, dòng 32)
│    out = None

▶ iam.base.ChangeEventSource   [0.0 ms]   (thread: MainThread, dòng 48)
│    out = None

▶ iam.keycloak.KeycloakAdmin   [0.0 ms]   (thread: MainThread, dòng 23)
│    out = None

▶ iam.keycloak.KeycloakAccessControl   [0.0 ms]   (thread: MainThread, dòng 116)
│    out = None

▶ iam.keycloak.KeycloakEventSource   [0.0 ms]   (thread: MainThread, dòng 150)
│    out = None

▶ access.Signature   [0.0 ms]   (thread: MainThread, dòng 25)
│    out = None

▶ tracing.Trace   [0.0 ms]   (thread: MainThread, dòng 16)
│    out = None

▶ chunking.Chunk   [0.0 ms]   (thread: MainThread, dòng 31)
│    out = None

▶ chunking._Section   [0.0 ms]   (thread: MainThread, dòng 44)
│    out = None

▶ cache.Provenance   [0.0 ms]   (thread: MainThread, dòng 33)
│    out = None

▶ cache.CacheEntry   [0.0 ms]   (thread: MainThread, dòng 43)
│    out = None

▶ cache.Candidate   [0.0 ms]   (thread: MainThread, dòng 75)
│    out = None

▶ cache.LookupResult   [0.0 ms]   (thread: MainThread, dòng 85)
│    out = None

▶ classifier.Classification   [0.0 ms]   (thread: MainThread, dòng 14)
│    out = None

▶ prompts.PromptError   [0.0 ms]   (thread: MainThread, dòng 12)
│    out = None

▶ llm.LLMResult   [0.0 ms]   (thread: MainThread, dòng 12)
│    out = None

▶ retrieval.Retrieved   [0.0 ms]   (thread: MainThread, dòng 17)
│    out = None

▶ pipeline.ChatResult   [0.0 ms]   (thread: MainThread, dòng 17)
│    out = None

▶ sync.PermissionSync   [0.0 ms]   (thread: MainThread, dòng 39)
│    out = None

▶ main.ChatIn   [0.1 ms]   (thread: MainThread, dòng 64)
│    out = None

▶ main.FeedbackIn   [0.0 ms]   (thread: MainThread, dòng 134)
│    out = None

▶ main.RoleIn   [0.0 ms]   (thread: MainThread, dòng 231)
│    out = None

▶ main.PublishIn   [0.0 ms]   (thread: MainThread, dòng 258)
│    out = None

▶ main.ResetIn   [0.0 ms]   (thread: MainThread, dòng 270)
│    out = None

▶ main.lifespan   [235.2 ms]   (thread: asyncio-portal-70175f51ca70, dòng 29)
│    in  _ = <FastAPI>
│  ▶ db.init_schema   [31.2 ms]   (thread: asyncio-portal-70175f51ca70, dòng 94)
│  │    out = None
│  ▶ prompts.validate   [4.7 ms]   (thread: asyncio-portal-70175f51ca70, dòng 58)
│  │    in  required = {rag_answer: {'history', 'context', 'question', 'no_answer'}}
│  │  ▶ prompts.variables   [4.7 ms]   (thread: asyncio-portal-70175f51ca70, dòng 32)
│  │  │    in  name = 'rag_answer'
│  │  │  ▶ prompts.get   [4.6 ms]   (thread: asyncio-portal-70175f51ca70, dòng 21)
│  │  │  │    in  name = 'rag_answer'
│  │  │  │    out = {description: 'Trả lời câu hỏi chỉ dựa trên ngữ cảnh đã lọc theo quyền, có trích dẫn nguồn.', temperature: 0.1, max_output_tokens: 600, system: 'Bạn là trợ lý hỏi đáp nội bộ của công ty Điện Máy Sao Mai.⏎Quy tắc bắt buộc:⏎1. Chỉ trả lời dựa trên NGỮ CẢNH được cung …(+298 ký tự)', user: '# NGỮ CẢNH⏎{context}⏎⏎# LỊCH SỬ HỘI THOẠI GẦN NHẤT (chỉ để hiểu câu hỏi, không phải nguồn thông tin)⏎{history}⏎⏎# CÂU HỎ…(+13 ký tự)'}
│  │  │    out = {'history', 'context', 'question', 'no_answer'}
│  │    out = None
│  ▶ documents.ensure_collection   [166.5 ms]   (thread: asyncio-portal-70175f51ca70, dòng 44)
│  │    out = None
│  ▶ cache.ensure_collection   [7.9 ms]   (thread: asyncio-portal-70175f51ca70, dòng 92)
│  │    out = None
│  ▶ sync.PermissionSync.__init__   [23.4 ms]   (thread: asyncio-portal-70175f51ca70, dòng 40)
│  │  ▶ iam.keycloak.KeycloakAdmin.__init__   [23.3 ms]   (thread: asyncio-portal-70175f51ca70, dòng 26)
│  │  │    in  realm = None
│  │  │    in  client_id = None
│  │  │    in  client_secret = None
│  │  │    out = None
│  │  ▶ iam.keycloak.KeycloakEventSource.__init__   [0.0 ms]   (thread: asyncio-portal-70175f51ca70, dòng 151)
│  │  │    in  admin = <KeycloakAdmin>
│  │  │    in  since_ms = 1794371838591
│  │  │    out = None
│  │    out = None
│  ▶ sync.PermissionSync.start   [1.0 ms]   (thread: asyncio-portal-70175f51ca70, dòng 48)
│  │    out = None
│    out = <async_generator_wrapped_value>

▶ sync.PermissionSync.poll_once   [? ms]   (thread: permission-sync, dòng 66)
│  ▶ iam.keycloak.KeycloakEventSource.poll   [? ms]   (thread: permission-sync, dòng 156)
│  │  ▶ iam.keycloak.KeycloakAdmin.admin_events   [? ms]   (thread: permission-sync, dòng 112)
│  │  │    in  max_results = 200
│  │  │  ▶ iam.keycloak.KeycloakAdmin.request   [? ms]   (thread: permission-sync, dòng 52)
│  │  │  │    in  method = 'GET'
│  │  │  │    in  path = '/admin-events'
│  │  │  │    in  kw = {params: {max: 200}}
│  │  │  │  ▶ iam.keycloak.KeycloakAdmin.token   [? ms]   (thread: permission-sync, dòng 39)
│  │  │  │  │    out = (chưa return)
│  │  │  │    out = (chưa return)
│  │  │    out = (chưa return)
│  │    out = (chưa return)
│    out = (chưa return)

```
