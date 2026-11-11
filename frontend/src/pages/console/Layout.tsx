import { useState } from 'react';
import { Link, NavLink, Route, Routes } from 'react-router-dom';
import { Me } from '../../api';
import { ThemeToggle, UserChip } from '../../components/ui';
import { useConsoleStream } from '../../stream';
import Admin from './Admin';
import CachePage from './Cache';
import Overview from './Overview';
import RequestDetail from './RequestDetail';
import Requests from './Requests';
import Security from './Security';

const NAV = [
  { to: '/console', label: 'Tổng quan', end: true },
  { to: '/console/requests', label: 'Request' },
  { to: '/console/cache', label: 'Cache' },
  { to: '/console/security', label: 'Bảo mật' },
  { to: '/console/admin', label: 'Quản trị' },
];

export default function ConsoleLayout({ me }: { me: Me }) {
  const [live, setLive] = useState<string | null>(null);
  useConsoleStream((type, d) => {
    if (type === 'trace') setLive(`${d.username}: ${d.status}`);
  });
  return (
    <div className="min-h-full p-4 flex flex-col gap-4">
      <header className="glass rounded-full flex items-center gap-4 pl-6 pr-2 py-2 flex-wrap">
        <div className="font-semibold">Console vận hành</div>
        <nav className="seg glass glass-strong" aria-label="Console">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => (isActive ? 'active' : '')}>{n.label}</NavLink>
          ))}
        </nav>
        <span className="faint text-sm flex items-center gap-2" aria-live="polite">
          <span className="inline-block w-2 h-2 rounded-full" style={{ background: 'var(--ok)' }} />
          {live ? `Mới nhất: ${live}` : 'Đang theo dõi realtime'}
        </span>
        <span className="flex-1" />
        <Link to="/chat" className="pill">Mở Chat</Link>
        <ThemeToggle />
        <UserChip name={me.name} username={me.username} />
      </header>
      <main className="flex-1">
        <Routes>
          <Route index element={<Overview />} />
          <Route path="requests" element={<Requests />} />
          <Route path="requests/:id" element={<RequestDetail />} />
          <Route path="cache" element={<CachePage />} />
          <Route path="security" element={<Security />} />
          <Route path="admin" element={<Admin me={me} />} />
        </Routes>
      </main>
    </div>
  );
}

export function Panel({ title, children, actions, className = '' }: { title?: string; children: React.ReactNode; actions?: React.ReactNode; className?: string }) {
  return (
    <section className={`glass glass-strong rounded-[24px] p-5 ${className}`}>
      {(title || actions) && (
        <div className="flex items-center justify-between gap-3 mb-3">
          {title && <h2 className="font-semibold text-[1.05rem]">{title}</h2>}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
