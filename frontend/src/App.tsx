import { lazy, Suspense, useEffect, useState } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { api, Me } from './api';
import ChatPage from './pages/Chat';

const ConsoleLayout = lazy(() => import('./pages/console/Layout'));

export default function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    api<Me>('/me').then(setMe).catch((e) => setErr(String(e.message ?? e)));
  }, []);

  if (err)
    return (
      <Centered>
        <h2 className="text-xl font-semibold">Không tải được thông tin tài khoản</h2>
        <p className="muted mt-2">Backend trả về: {err}. Kiểm tra backend đang chạy ở cổng 8000 rồi tải lại trang.</p>
      </Centered>
    );
  if (!me) return <Centered><p className="muted">Đang tải…</p></Centered>;

  return (
    <>
      <div className="backdrop" aria-hidden />
      <Routes>
        <Route path="/" element={<Navigate to={me.is_console ? '/console' : '/chat'} replace />} />
        <Route path="/chat" element={<ChatPage me={me} />} />
        <Route path="/chat/:sessionId" element={<ChatPage me={me} />} />
        <Route
          path="/console/*"
          element={
            me.is_console ? (
              <Suspense fallback={<Centered><p className="muted">Đang tải Console…</p></Centered>}>
                <ConsoleLayout me={me} />
              </Suspense>
            ) : (
              <Forbidden />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-full grid place-items-center p-6">
      <div className="backdrop" aria-hidden />
      <div className="glass rounded-3xl p-8 max-w-lg">{children}</div>
    </div>
  );
}

function Forbidden() {
  return (
    <Centered>
      <h1 className="text-2xl font-semibold" data-testid="forbidden">Bạn không có quyền vào Console</h1>
      <p className="muted mt-2">Console chỉ dành cho tài khoản có vai trò vận hành (ops_admin). Bạn vẫn dùng trợ lý hỏi đáp bình thường.</p>
      <a href="/chat" className="pill pill-primary mt-5">Về trang hỏi đáp</a>
    </Centered>
  );
}
