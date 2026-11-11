import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api, SecurityEvent } from '../../api';
import { fmtTime } from '../../components/ui';
import { useConsoleStream } from '../../stream';
import { Panel } from './Layout';

interface SecData {
  events: SecurityEvent[];
  revocation: { n: number; avg_s: number | null; max_s: number | null };
  unauthorized_traces: { id: string; created_at: string; username: string; question: string; audit: any }[];
}

const KIND: Record<string, string> = { permission_change: 'Đổi quyền', doc_update: 'Sửa tài liệu' };

export default function Security() {
  const [d, setD] = useState<SecData | null>(null);
  const load = useCallback(() => api<SecData>('/console/security/events').then(setD).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  useConsoleStream((type) => { if (type === 'security' || type === 'audit') load(); });
  if (!d) return <p className="muted p-4">Đang tải…</p>;
  const bad = d.unauthorized_traces.length;
  return (
    <div className="grid gap-4">
      <div className="grid gap-4 md:grid-cols-2">
        <Panel>
          <div className="muted text-sm">Câu trả lời vượt quyền (phát hiện bằng canary)</div>
          <div className="text-[2.2rem] font-semibold" style={{ color: bad ? 'var(--danger)' : 'var(--ok)' }} data-testid="security-unauthorized">{bad}</div>
          <p className="faint text-xs">{bad ? 'Cần điều tra ngay: xem danh sách bên dưới.' : 'Mục tiêu là 0. Mỗi câu trả lời đều được kiểm tra lại với IAM.'}</p>
        </Panel>
        <Panel>
          <div className="muted text-sm">Thời gian từ lúc đổi quyền đến khi hệ thống áp dụng</div>
          <div className="text-[2.2rem] font-semibold">{d.revocation.avg_s == null ? '–' : `${d.revocation.avg_s.toFixed(2)} s`}</div>
          <p className="faint text-xs">{d.revocation.max_s == null ? 'Chưa có sự kiện đổi quyền.' : `Chậm nhất ${d.revocation.max_s.toFixed(2)} s trên ${d.revocation.n} sự kiện. Muốn nhanh hơn: giảm chu kỳ đọc sự kiện Keycloak.`}</p>
        </Panel>
      </div>
      {bad > 0 && (
        <Panel title="Câu trả lời vượt quyền">
          <ul className="grid gap-2">{d.unauthorized_traces.map((t) => (
            <li key={t.id}><Link to={`/console/requests/${t.id}`} style={{ color: 'var(--danger)' }}>{fmtTime(t.created_at)} {t.username}: {t.question}</Link></li>
          ))}</ul>
        </Panel>
      )}
      <Panel title="Dòng thời gian thay đổi quyền và tài liệu">
        <table className="data" data-testid="security-events">
          <thead><tr><th>Xảy ra lúc</th><th>Loại</th><th>Nguồn</th><th>Nội dung</th><th>Có hiệu lực sau</th></tr></thead>
          <tbody>
            {d.events.length === 0 && <tr><td colSpan={5} className="faint">Chưa có thay đổi nào. Thử thu hồi một quyền ở trang Quản trị.</td></tr>}
            {d.events.map((e) => (
              <tr key={e.id} data-testid="security-event" data-kind={e.kind}>
                <td className="whitespace-nowrap">{fmtTime(e.occurred_at)}</td>
                <td>{KIND[e.kind] ?? e.kind}</td>
                <td className="muted">{e.source === 'keycloak' ? 'Keycloak' : 'Trang quản trị'}</td>
                <td>{e.summary}</td>
                <td>{e.window_seconds == null ? '–' : `${e.window_seconds.toFixed(2)} s`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
