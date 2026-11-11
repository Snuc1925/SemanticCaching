/**
 * Kịch bản "luồng hoàn chỉnh" (plan mục 11.1) chạy trên hệ thống thật.
 * Các bước phụ thuộc nhau (cache được tạo ở bước trước) nên chạy tuần tự (serial).
 */
import { expect, Page, test } from '@playwright/test';
import { ask, CANARY_VIP, loginAs, resetDemo } from './helpers';

test.describe.configure({ mode: 'serial' });

const Q_VIP = 'Khách VIP được đổi trả trong bao lâu?';
const Q_VIP_PARA = 'Thời hạn đổi trả hàng cho khách VIP là bao lâu?';
const Q_RETURN = 'Chính sách đổi trả cho phép trả hàng trong mấy ngày?';
const Q_RETURN_PARA = 'Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?';

let cskh1: Page, cskh2: Page, khach: Page, admin: Page;

test.beforeAll(async ({ browser }) => {
  await resetDemo();
  cskh1 = await loginAs(browser, 'cskh1', '/chat');
  cskh2 = await loginAs(browser, 'cskh2', '/chat');
  khach = await loginAs(browser, 'khach', '/chat');
  admin = await loginAs(browser, 'admin_ops');
});

test.afterAll(async () => {
  await resetDemo();
});

test('1. Đăng nhập và hỏi lần đầu: sinh mới (MISS), có trích dẫn, Console ghi nhận', async () => {
  const r = await ask(cskh1, Q_VIP);
  expect(r.status).toBe('MISS');
  expect(r.text).toMatch(/33/);
  await admin.goto('/console/requests');
  const row = admin.getByTestId('request-row').filter({ hasText: Q_VIP }).first();
  await expect(row).toBeVisible();
  await expect(row.getByTestId('cache-badge')).toHaveAttribute('data-status', 'MISS');
});

test('2. Diễn đạt khác, user khác cùng quyền: trả từ cache (HIT), Console hiện entry được chọn', async () => {
  const r = await ask(cskh2, Q_VIP_PARA);
  expect(r.status).toBe('HIT');
  await admin.goto('/console/requests');
  await admin.getByTestId('request-row').filter({ hasText: Q_VIP_PARA }).first().click();
  await expect(admin.getByTestId('trace-question')).toHaveText(Q_VIP_PARA);
  await expect(admin.getByTestId('candidates')).toContainText('thoả mọi điều kiện');
  await expect(admin.getByTestId('span-cache_hit')).toBeVisible();
});

test('3. User công khai hỏi cùng câu: không dùng chéo cache, không lộ thông tin CSKH', async () => {
  const r = await ask(khach, Q_VIP);
  expect(r.status).not.toBe('HIT');
  expect(r.text).not.toMatch(CANARY_VIP);
});

test('4. Thu hồi quyền CSKH trên Console: câu trả lời sau đó không còn thông tin CSKH', async () => {
  await admin.goto('/console/admin');
  await admin.getByTestId('role-cskh1-cskh_agent').click();
  await expect(admin.getByTestId('admin-message')).toContainText('Đã thu hồi');
  await admin.waitForTimeout(4000); // > chu kỳ đọc admin-events (2 s)
  const r = await ask(cskh1, Q_VIP_PARA);
  expect(r.status).not.toBe('HIT');
  expect(r.text).not.toMatch(CANARY_VIP);
  await admin.goto('/console/security');
  await expect(admin.getByTestId('security-event').filter({ hasText: 'REALM_ROLE_MAPPING' }).first()).toBeVisible();
});

test('5. Sửa tài liệu lên v2: entry cũ bị xoá, câu trả lời mới dùng nội dung mới', async () => {
  const a = await ask(khach, Q_RETURN);
  expect(a.text).toMatch(/\b7\b/);
  const b = await ask(khach, Q_RETURN_PARA);
  expect(b.status).toBe('HIT');
  await admin.goto('/console/admin');
  await admin.getByTestId('publish-return_policy-v2').click();
  await expect(admin.getByTestId('admin-message')).toContainText('Đã xuất bản return_policy v2');
  const c = await ask(khach, Q_RETURN_PARA);
  expect(c.status).toBe('MISS');
  expect(c.text).toMatch(/15/);
  await admin.goto('/console/security');
  await expect(admin.getByTestId('security-event').filter({ hasText: 'return_policy: v1 -> v2' }).first()).toBeVisible();
});

test('6. Câu cá nhân và câu nối tiếp không dùng cache', async () => {
  expect((await ask(khach, 'Đơn hàng của tôi đang ở đâu rồi?')).status).toBe('NO_CACHE');
  expect((await ask(khach, 'Thế còn hàng điện tử thì sao?')).status).toBe('BYPASS');
});

test('7. Console tổng quan: có số liệu, không có câu trả lời vượt quyền; user thường không vào được Console', async () => {
  await admin.goto('/console');
  await expect(admin.getByTestId('stat-requests-value')).not.toHaveText('0');
  await admin.waitForTimeout(1500); // audit chạy nền sau mỗi câu trả lời
  await admin.reload();
  await expect(admin.getByTestId('stat-unauthorized-value')).toHaveText('0');
  await khach.goto('/console');
  await expect(khach.getByTestId('forbidden')).toBeVisible();
});
