# Cài đặt và chạy

## Yêu cầu
- Docker và Docker Compose v2+ (đã thử với Docker 29, Compose v5).
- Python 3.12 (có `venv`).
- Node 22 qua nvm (`nvm install 22`). Node 18 không chạy được Vite 6.
- API key: OpenAI (embedding) và Gemini (LLM).
- RAM trống khoảng 3 GB cho Keycloak, Postgres, Qdrant, Redis.

Các cổng dùng: 5432 (Postgres), 8080 (Keycloak), 6333 (Qdrant), 6379 (Redis), 8000 (backend), 5173 (frontend).

## Cách 1: phát triển (hạ tầng trong Docker, backend/frontend chạy ngoài)
```bash
cp .env.example .env                 # điền OPENAI_API_KEY, GEMINI_API_KEY
make venv                            # tạo .venv và cài node_modules (1 lần)
make check-apis                      # kiểm tra 2 key, in id model Gemini truy cập được
make infra-up                        # chạy 4 container, chờ Keycloak healthy
make setup                           # tạo realm Keycloak + nạp 10 tài liệu pilot
make dev-backend                     # terminal 1: http://localhost:8000 (hot reload)
make dev-frontend                    # terminal 2: http://localhost:5173
```
Mở http://localhost:5173 và đăng nhập.

## Cách 2: toàn bộ trong Docker (demo / nộp bài)
```bash
cp .env.example .env                 # điền key
make infra-up
make app-up                          # build và chạy backend + frontend
make app-setup                       # tạo realm + nạp dữ liệu (chạy trong container backend)
```
Mở http://localhost:5173. Dừng bằng `make infra-down`.

## Tài khoản demo (mật khẩu chung `demo1234`)
| User | Vai trò | Đọc được | Dùng để |
|---|---|---|---|
| `khach` | customer | Công khai | Thử người ít quyền nhất |
| `cskh1`, `cskh2` | employee, cskh_agent | Công khai, Nội bộ, CSKH | Cùng signature, thử HIT dùng chung |
| `sales_bac` | employee, sales, region=north | + Kinh doanh miền Bắc | ABAC theo miền |
| `sales_nam` | employee, sales, region=south | + Kinh doanh miền Nam | ABAC theo miền |
| `hr1` | employee, hr | + Nhân sự (mật) | |
| `admin_ops` | employee, ops_admin | Công khai, Nội bộ | **Vào Console** |

Keycloak admin console: http://localhost:8080 (`admin` / `admin`), realm `semcache`.

Muốn vừa chat vừa xem Console cùng lúc: mở **2 cửa sổ tách phiên** (một cửa sổ thường, một cửa sổ ẩn danh), vì cùng trình duyệt sẽ dùng chung phiên đăng nhập.

## Khôi phục trạng thái demo
- Trên Console → Quản trị → **Khôi phục dữ liệu demo**: đưa quyền về như `acl.yaml`, tài liệu về v1, xoá cache (giữ lịch sử).
- Xoá sạch cả lịch sử: `make seed`.
- Tạo lại hoàn toàn realm Keycloak: `make keycloak`.

## Lỗi thường gặp
| Hiện tượng | Cách xử lý |
|---|---|
| Trang trắng, báo "Không kết nối được máy chủ đăng nhập" | Keycloak chưa chạy hoặc chưa healthy: `make infra-up` |
| "Không tải được thông tin tài khoản" | Backend chưa chạy ở :8000, hoặc realm chưa được tạo (`make keycloak`) |
| Đăng nhập báo sai realm hoặc client | Chạy lại `make keycloak` (realm bị xoá khi xoá volume Postgres) |
| Backend báo lỗi Gemini 404 model | Sửa `LLM_MODEL` trong `.env` theo danh sách mà `make check-apis` in ra |
| Vite báo lỗi cú pháp lạ | Đang dùng Node 18: `nvm use 22` |
| Playwright tải lại trình duyệt mỗi lần | Không đổi phiên bản `@playwright/test` (đã ghim 1.65.0), chỉ chạy `make e2e-install` một lần |
| Thu hồi quyền mà Console chưa có sự kiện | Kiểm tra `GET /api/health`: `sync_error` phải là `null` |
