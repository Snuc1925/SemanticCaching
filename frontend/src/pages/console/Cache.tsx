import { useCallback, useEffect, useState } from 'react';
import { api } from '../../api';
import { useConsoleStream } from '../../stream';
import { Panel } from './Layout';

interface Entry {
  entry_id: string; partition: string; question: string; intent: string; policy: string; hits: number;
  provenance: { doc_id: string; version: number; collection: string }[]; ttl_left: number; created_at: number;
}
interface CacheData { stats: Record<string, number>; partitions: Record<string, string[]>; entries: Entry[] }

export default function CachePage() {
  const [d, setD] = useState<CacheData | null>(null);
  const load = useCallback(() => api<CacheData>('/console/cache/entries').then(setD).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  useConsoleStream((type) => { if (type === 'trace' || type === 'security') load(); });

  async function flush() {
    if (!confirm('Xoá toàn bộ cache? Các câu hỏi tiếp theo sẽ phải sinh lại bằng LLM.')) return;
    await api('/console/cache', { method: 'DELETE' });
    load();
  }
  if (!d) return <p className="muted p-4">Đang tải…</p>;
  return (
    <div className="grid gap-4 lg:grid-cols-[20rem_minmax(0,1fr)]">
      <div className="grid gap-4 content-start">
        <Panel title="Tình trạng">
          <dl className="grid grid-cols-2 gap-y-1 text-sm">
            <dt className="muted">Số entry</dt><dd data-testid="cache-entries-count">{d.stats.entries ?? 0}</dd>
            <dt className="muted">Xoá do sửa tài liệu</dt><dd>{d.stats.invalidated_doc_update ?? 0}</dd>
            <dt className="muted">Loại do đầy (LRU)</dt><dd>{d.stats.evicted_lru ?? 0}</dd>
          </dl>
          <button className="pill pill-danger mt-4" onClick={flush}>Xoá toàn bộ cache</button>
        </Panel>
        <Panel title="Partition">
          <p className="faint text-xs mb-2">Mỗi partition là một tập quyền. User cùng partition dùng chung cache.</p>
          <ul className="grid gap-2 text-sm">
            {Object.entries(d.partitions).map(([sig, users]) => (
              <li key={sig}><div className="font-medium">{sig}</div><div className="muted">{users.join(', ')}</div></li>
            ))}
          </ul>
        </Panel>
      </div>
      <Panel title="Entry trong cache">
        <div className="overflow-x-auto">
          <table className="data">
            <thead><tr><th>Câu hỏi</th><th>Partition</th><th>Intent</th><th>Lượt dùng lại</th><th>Nguồn</th><th>Còn hạn</th></tr></thead>
            <tbody>
              {d.entries.length === 0 && <tr><td colSpan={6} className="faint">Cache đang trống. Câu hỏi đủ điều kiện sẽ được lưu sau lần trả lời đầu tiên.</td></tr>}
              {d.entries.map((e) => (
                <tr key={e.entry_id}>
                  <td>{e.question}</td><td>{e.partition}</td><td>{e.intent}</td><td>{e.hits}</td>
                  <td>{[...new Set(e.provenance.map((p) => `${p.doc_id} v${p.version}`))].join(', ')}</td>
                  <td>{e.ttl_left > 3600 ? `${Math.round(e.ttl_left / 3600)} giờ` : `${Math.round(e.ttl_left / 60)} phút`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
