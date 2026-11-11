import { defineConfig } from '@playwright/test';

/**
 * E2E chạy trên hệ thống THẬT (Keycloak, backend, Gemini, OpenAI). Cần chạy trước:
 *   make infra-up && make seed && make dev-backend && make dev-frontend
 * Test chạy tuần tự (workers=1) vì các kịch bản thay đổi trạng thái chung (quyền, tài liệu, cache).
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 120_000,
  expect: { timeout: 30_000 },
  workers: 1,
  fullyParallel: false,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    locale: 'vi-VN',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    viewport: { width: 1440, height: 900 },
  },
});
