# Dùng: make <target>. Cần Docker, Python 3.12, Node 22 (nvm).
SHELL := /bin/bash
PY    := .venv/bin/python
NODE  := source ~/.nvm/nvm.sh >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1;

.PHONY: help venv infra-up infra-down keycloak seed setup dev-backend dev-frontend check-apis test smoke e2e e2e-install screenshots trace app-up app-setup

help: ## Liệt kê các lệnh
	@grep -E '^[a-z0-9-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-14s %s\n", $$1, $$2}'

venv: ## Tạo .venv, cài thư viện backend và frontend
	python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q -r backend/requirements.txt
	cd frontend && $(NODE) npm ci

infra-up: ## Chạy Postgres, Keycloak, Qdrant, Redis (Docker)
	docker compose up -d postgres keycloak qdrant redis
	@echo "Chờ Keycloak sẵn sàng..."; until [ "$$(docker inspect -f '{{.State.Health.Status}}' semcache-keycloak-1)" = healthy ]; do sleep 2; done; echo OK

infra-down: ## Dừng hạ tầng (giữ dữ liệu)
	docker compose --profile app down

keycloak: ## Cấu hình Keycloak từ data/pilot/acl.yaml (tạo lại realm)
	$(PY) scripts/setup_keycloak.py

seed: ## Nạp tài liệu pilot vào Qdrant, xoá cache và lịch sử
	$(PY) scripts/seed.py --clear-history

setup: keycloak seed ## keycloak + seed

check-apis: ## Kiểm tra key OpenAI/Gemini trong .env
	$(PY) scripts/check_apis.py

dev-backend: ## Chạy backend (hot reload) ở :8000
	cd backend && ../.venv/bin/uvicorn app.main:app --port 8000 --reload

dev-frontend: ## Chạy frontend (Vite) ở :5173
	cd frontend && $(NODE) npm run dev

test: ## Unit test backend (không gọi API ngoài)
	.venv/bin/pytest -q tests

smoke: ## Smoke test luồng hoàn chỉnh qua API (cần backend đang chạy)
	$(PY) scripts/smoke_api.py

e2e-install: ## Cài trình duyệt Chromium cho Playwright (1 lần)
	cd frontend && $(NODE) npx playwright install chromium

e2e: ## Playwright e2e 7 kịch bản (cần backend + frontend đang chạy)
	cd frontend && $(NODE) npx playwright test e2e/flow.spec.ts

screenshots: ## Chụp màn hình giao diện vào docs/screenshots (cần hệ thống đang chạy)
	cd frontend && $(NODE) SHOTS_DIR=$(CURDIR)/docs/screenshots npx playwright test e2e/screenshots.spec.ts

trace: ## Ghi lại lời gọi hàm của các kịch bản backend vào docs/walkthrough/raw (gọi API thật)
	$(PY) scripts/walkthrough/trace_calls.py --src backend/app --scenarios scripts/walkthrough/scenarios.py --out docs/walkthrough/raw

app-up: ## Chạy TOÀN BỘ trong Docker (demo / nộp bài)
	docker compose --profile app up -d --build

app-setup: ## Cấu hình Keycloak + seed khi chạy toàn bộ trong Docker
	docker compose exec backend python /app/scripts/setup_keycloak.py
	docker compose exec backend python /app/scripts/seed.py --clear-history
	docker compose restart backend
