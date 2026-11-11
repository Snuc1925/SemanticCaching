import { Browser, expect, Page } from '@playwright/test';

export const PASSWORD = 'demo1234';
const API = process.env.E2E_API_URL ?? 'http://localhost:8000';
const KC = process.env.E2E_KEYCLOAK_URL ?? 'http://localhost:8080';

/** Mỗi user một browser context riêng (giống mở cửa sổ ẩn danh), đăng nhập qua form Keycloak thật. */
export async function loginAs(browser: Browser, username: string, path = '/'): Promise<Page> {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(path);
  await page.locator('#username').fill(username);
  await page.locator('#password').fill(PASSWORD);
  await page.locator('#kc-login').click();
  await expect(page.getByTestId('current-user').first()).toBeVisible();
  return page;
}

/** Gửi câu hỏi trong trang Chat, chờ câu trả lời mới, trả về {status, text}. */
export async function ask(page: Page, question: string) {
  const before = await page.getByTestId('assistant-message').count();
  await page.getByTestId('chat-input').fill(question);
  await page.getByTestId('send').click();
  const msg = page.getByTestId('assistant-message').nth(before);
  await expect(msg).toBeVisible({ timeout: 90_000 });
  const status = await msg.getByTestId('cache-badge').getAttribute('data-status');
  const text = (await msg.getByTestId('answer-text').innerText()).trim();
  return { status, text };
}

async function adminToken(): Promise<string> {
  const r = await fetch(`${KC}/realms/semcache/protocol/openid-connect/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'password', client_id: 'semcache-frontend', username: 'admin_ops', password: PASSWORD }),
  });
  return (await r.json()).access_token;
}

/** Đưa hệ thống về trạng thái ban đầu (quyền theo acl.yaml, tài liệu v1, cache rỗng). */
export async function resetDemo() {
  const r = await fetch(`${API}/api/console/admin/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${await adminToken()}` },
    body: JSON.stringify({ clear_history: false }),
  });
  if (!r.ok) throw new Error(`reset lỗi ${r.status}`);
  await new Promise((res) => setTimeout(res, 3000)); // để poller xử lý các event đổi quyền của reset
}

export const CANARY_VIP = /\b(33|47)\s*ngày|VIP-RT-47/;
