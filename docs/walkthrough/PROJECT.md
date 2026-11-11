# Cấu hình walkthrough của project semantic-cache

File này dành cho skill `walkthrough` (`~/.claude/skills/walkthrough`). Skill đọc file này trước khi làm việc trong project.

## Các file
| Gì | Đường dẫn (từ `semantic-cache/src/`) |
|---|---|
| Mã nguồn cần ghi | `backend/app` |
| Kịch bản | `scripts/walkthrough/scenarios.py` |
| Bộ ghi (bản chép trong repo) | `scripts/walkthrough/trace_calls.py`, `scripts/walkthrough/inventory.py` |
| Bản ghi thô | `docs/walkthrough/raw/` |
| Tài liệu luồng | `docs/WALKTHROUGH.md` |
| Từ điển | `docs/DICTIONARY.md` |

## Lệnh
```bash
docker ps                      # trống → make infra-up
make setup                     # nếu realm Keycloak / dữ liệu chưa có
make trace                     # ghi lại 10 kịch bản (gọi OpenAI + Gemini thật, vài nghìn token)
.venv/bin/python scripts/walkthrough/trace_calls.py --src backend/app \
    --scenarios scripts/walkthrough/scenarios.py --out docs/walkthrough/raw --render-only   # chỉ dựng lại .md
python3 scripts/walkthrough/inventory.py backend/app --check docs/WALKTHROUGH.md          # hàm chưa được nhắc
```
Kiểm chứng một khẳng định bằng span đã lưu:
```python
import sys; sys.path.insert(0, 'backend')
from app import db
db.fetch_one("SELECT spans FROM traces WHERE question LIKE %s ORDER BY created_at DESC LIMIT 1", ('Đơn hàng%',))
```

## Phạm vi
- Chỉ luồng **backend**, kể cả các endpoint Console tác động lên backend. Frontend không thuộc phạm vi.
- Người dùng muốn hiểu kỹ **IAM/Keycloak**: giữ mục IAM với dữ liệu thật (claims token, request/response `policy/evaluate`, admin event).
- Ngôn ngữ tài liệu: tiếng Việt.

## Bẫy riêng của project
- Keycloak 26.0 không trả `id` cho admin event → khoá chống trùng là `_event_key`.
- Sau khi máy khởi động lại, container dừng hết; `curl` tới cổng đã đóng có thể treo → luôn dùng `timeout`.
- `pkill -f uvicorn…` có thể giết chính shell → dùng PID file / `ss -ltnp`.
- Kịch bản `06_revoke` cần `wait` > chu kỳ poll (2 s); revocation window dao động 0–2 s tuỳ thời điểm.
- Thời gian gọi OpenAI dao động mạnh (240–850 ms cho một câu) → khi so sánh latency giữa các lần chạy, ghi rõ.
