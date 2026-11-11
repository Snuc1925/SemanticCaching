import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, CacheStatus, TraceSummary } from '../../api';
import { fmtMs, fmtTime, fmtUsd, StatusBadge } from '../../components/ui';
import { useConsoleStream } from '../../stream';
import { Panel } from './Layout';

const FILTERS: (CacheStatus | 'ALL')[] = ['ALL', 'HIT', 'MISS', 'BYPASS', 'NO_CACHE', 'ERROR'];

export default function Requests() {
  const [rows, setRows] = useState<TraceSummary[]>([]);
  const [filter, setFilter] = useState<CacheStatus | 'ALL'>('ALL');
  const nav = useNavigate();

  useEffect(() => {
    api<TraceSummary[]>(`/console/traces?limit=200${filter === 'ALL' ? '' : `&status=${filter}`}`).then(setRows).catch(() => {});
  }, [filter]);

  useConsoleStream((type, d) => {
    if (type === 'trace' && (filter === 'ALL' || d.status === filter)) setRows((r) => [d, ...r.filter((x) => x.id !== d.id)].slice(0, 200));
    if (type === 'audit') setRows((r) => r.map((x) => (x.id === d.id ? { ...x, unauthorized: d.unauthorized } : x)));
  });

  return (
    <Panel
      title="Request gần đây"
      actions={
        <div className="seg glass">
          {FILTERS.map((f) => (
            <a key={f} href="#" className={filter === f ? 'active' : ''} onClick={(e) => { e.preventDefault(); setFilter(f); }}>
              {f === 'ALL' ? 'Tất cả' : f}
            </a>
          ))}
        </div>
      }
    >
      <div className="overflow-x-auto">
        <table className="data" data-testid="requests-table">
          <thead>
            <tr><th>Thời gian</th><th>User</th><th>Câu hỏi</th><th>Kết quả</th><th>Similarity</th><th>Độ trễ</th><th>Token LLM</th><th>Chi phí</th><th>Tiết kiệm</th><th>Audit</th></tr>
          </thead>
          <tbody>
            {rows.length === 0 && <tr><td colSpan={10} className="faint">Chưa có request. Đặt câu hỏi ở trang Chat để thấy request xuất hiện tại đây.</td></tr>}
            {rows.map((r) => (
              <tr key={r.id} className="clickable" onClick={() => nav(`/console/requests/${r.id}`)} data-testid="request-row">
                <td className="whitespace-nowrap">{fmtTime(r.created_at)}</td>
                <td>{r.username}</td>
                <td className="max-w-[28rem]"><div className="ellipsis">{r.question}</div></td>
                <td><StatusBadge status={r.status} /></td>
                <td>{r.similarity == null ? '–' : r.similarity.toFixed(3)}</td>
                <td>{fmtMs(r.latency_ms)}</td>
                <td>{r.llm_tokens_in + r.llm_tokens_out || '–'}</td>
                <td>{fmtUsd(r.cost_usd)}</td>
                <td style={{ color: r.saved_tokens ? 'var(--hit)' : undefined }}>{r.saved_tokens ? `${r.saved_tokens} token` : '–'}</td>
                <td>{r.unauthorized == null ? <span className="faint">…</span> : r.unauthorized ? <span style={{ color: 'var(--danger)' }}>Vượt quyền</span> : <span style={{ color: 'var(--ok)' }}>Sạch</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}
