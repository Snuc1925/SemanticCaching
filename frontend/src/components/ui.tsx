import { useEffect, useState } from 'react';
import { CacheStatus } from '../api';
import { logout } from '../auth';

export const STATUS_LABEL: Record<CacheStatus, string> = {
  HIT: 'Từ cache',
  MISS: 'Sinh mới',
  BYPASS: 'Không dùng cache',
  NO_CACHE: 'Không cache',
  ERROR: 'Lỗi',
};

export const COLLECTION_LABEL: Record<string, string> = {
  public: 'Công khai',
  internal_all: 'Nội bộ chung',
  cskh: 'CSKH',
  hr_confidential: 'Nhân sự (mật)',
  sales_north: 'Kinh doanh miền Bắc',
  sales_south: 'Kinh doanh miền Nam',
};

export function StatusBadge({ status, title }: { status: CacheStatus; title?: string }) {
  return (
    <span className={`badge badge-${status}`} title={title} data-testid="cache-badge" data-status={status}>
      {status === 'HIT' && <Star />}
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

function Star() {
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" aria-hidden fill="currentColor">
      <path d="M12 2l2.6 7.4H22l-6 4.6 2.3 7.4L12 16.8 5.7 21.4 8 14 2 9.4h7.4z" />
    </svg>
  );
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<string>(() => {
    try { return localStorage.getItem('theme') ?? 'auto'; } catch { return 'auto'; }
  });
  useEffect(() => {
    const el = document.documentElement;
    if (theme === 'auto') el.removeAttribute('data-theme');
    else el.setAttribute('data-theme', theme);
    try { localStorage.setItem('theme', theme); } catch { /* bỏ qua */ }
  }, [theme]);
  const next = theme === 'auto' ? 'light' : theme === 'light' ? 'dark' : 'auto';
  const label = theme === 'auto' ? 'Giao diện: theo hệ thống' : theme === 'light' ? 'Giao diện: sáng' : 'Giao diện: tối';
  return (
    <button className="pill" onClick={() => setTheme(next)} title="Đổi giao diện sáng/tối" aria-label={label}>
      {theme === 'dark' ? '☾' : theme === 'light' ? '☀' : '◐'}
    </button>
  );
}

export function UserChip({ name, username }: { name: string; username: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="text-right leading-tight">
        <div className="font-semibold text-sm" data-testid="current-user">{name || username}</div>
        <div className="faint text-xs">{username}</div>
      </div>
      <button className="pill" onClick={logout}>Đăng xuất</button>
    </div>
  );
}

export function fmtMs(ms: number | null | undefined) {
  if (ms == null) return '–';
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${Math.round(ms)} ms`;
}
export function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}
export function fmtUsd(v: number | null | undefined) {
  if (v == null) return '–';
  return v < 0.01 ? `$${v.toFixed(5)}` : `$${v.toFixed(3)}`;
}
