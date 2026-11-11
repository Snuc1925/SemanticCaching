import { useCallback, useEffect, useState } from 'react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../../api';
import { fmtMs, fmtUsd } from '../../components/ui';
import { useConsoleStream } from '../../stream';
import { Panel } from './Layout';

interface Overview {
  totals: Record<string, number>;
  hit_rate: number | null;
  false_hit_rate_feedback: number | null;
  latency: Record<string, { n: number; p50: number; p95: number }>;
  series: { t: string; requests: number; hits: number; misses: number; avg_latency: number }[];
  by_intent: { intent: string; requests: number; hits: number; misses: number; hit_negative_feedback: number; avg_hit_similarity: number | null }[];
  cache: Record<string, number>;
  partitions: Record<string, string[]>;
  revocation: { n: number; avg_s: number | null; max_s: number | null };
}

const pct = (v: number | null | undefined) => (v == null ? '–' : `${(v * 100).toFixed(1)}%`);

export default function OverviewPage() {
  const [d, setD] = useState<Overview | null>(null);
  const load = useCallback(() => api<Overview>('/console/metrics/overview').then(setD).catch(() => {}), []);
  useEffect(() => { load(); }, [load]);
  useConsoleStream((type) => { if (type !== 'ping') load(); });
  if (!d) return <p className="muted p-4">Đang tải số liệu…</p>;
  const t = d.totals;
  const unauthorized = t.unauthorized ?? 0;
  return (
    <div className="grid gap-4">
      <div className="grid gap-4 grid-cols-2 md:grid-cols-3 xl:grid-cols-6">
        <Stat label="Tỷ lệ trả từ cache" value={pct(d.hit_rate)} hint={`${t.hits} hit / ${t.hits + t.misses} câu được phép cache`} tone="hit" testid="stat-hit-rate" />
        <Stat label="Tổng request" value={String(t.requests)} hint={`${t.bypass + t.no_cache} câu không dùng cache`} testid="stat-requests" />
        <Stat label="Token LLM tiết kiệm" value={t.saved_tokens.toLocaleString('vi-VN')} hint={`đã dùng ${t.llm_tokens.toLocaleString('vi-VN')} token`} tone="hit" />
        <Stat label="Chi phí tiết kiệm" value={fmtUsd(t.saved_cost_usd)} hint={`đã chi ${fmtUsd(t.cost_usd)}`} />
        <Stat label="Trả lời vượt quyền" value={String(unauthorized)} hint={`audit ${t.audited} câu trả lời bằng canary`} tone={unauthorized ? 'danger' : 'ok'} testid="stat-unauthorized" />
        <Stat label="Thời gian thu hồi quyền có hiệu lực" value={d.revocation.avg_s == null ? '–' : `${d.revocation.avg_s.toFixed(2)} s`} hint={d.revocation.max_s == null ? 'chưa có sự kiện' : `tối đa ${d.revocation.max_s.toFixed(2)} s, ${d.revocation.n} sự kiện`} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <Panel title="Request theo phút">
          <div className="h-64">
            {d.series.length === 0 ? <Empty text="Chưa có request nào. Mở Chat và đặt câu hỏi để thấy số liệu." /> : (
              <ResponsiveContainer>
                <AreaChart data={d.series.map((s) => ({ ...s, label: new Date(s.t).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) }))}>
                  <CartesianGrid stroke="var(--line)" vertical={false} />
                  <XAxis dataKey="label" stroke="var(--ink-faint)" fontSize={12} />
                  <YAxis allowDecimals={false} stroke="var(--ink-faint)" fontSize={12} width={28} />
                  <Tooltip contentStyle={{ background: 'var(--glass-strong)', border: '1px solid var(--glass-edge)', borderRadius: 14 }} />
                  <Area type="monotone" dataKey="hits" name="Từ cache" stackId="1" stroke="var(--hit)" fill="var(--hit)" fillOpacity={0.35} />
                  <Area type="monotone" dataKey="misses" name="Sinh mới" stackId="1" stroke="var(--miss)" fill="var(--miss)" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </Panel>
        <Panel title="Độ trễ">
          <table className="data">
            <thead><tr><th>Loại</th><th>Số câu</th><th>p50</th><th>p95</th></tr></thead>
            <tbody>
              {Object.entries(d.latency).map(([k, v]) => (
                <tr key={k}><td><span className={`badge badge-${k}`}>{k}</span></td><td>{v.n}</td><td>{fmtMs(v.p50)}</td><td>{fmtMs(v.p95)}</td></tr>
              ))}
            </tbody>
          </table>
          <p className="faint text-xs mt-3">HIT nhanh hơn MISS vì bỏ qua retrieval và lời gọi LLM.</p>
        </Panel>
      </div>

      <Panel title="Theo nhóm câu hỏi (intent)">
        <table className="data">
          <thead><tr><th>Intent</th><th>Request</th><th>Hit</th><th>Miss</th><th>Hit bị chê</th><th>Similarity TB khi hit</th><th>Gợi ý</th></tr></thead>
          <tbody>
            {d.by_intent.map((r) => (
              <tr key={r.intent}>
                <td>{r.intent}</td><td>{r.requests}</td><td>{r.hits}</td><td>{r.misses}</td><td>{r.hit_negative_feedback}</td>
                <td>{r.avg_hit_similarity?.toFixed(3) ?? '–'}</td>
                <td className="muted">{advice(r)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}

function advice(r: Overview['by_intent'][number]) {
  if (r.hits > 0 && r.hit_negative_feedback / r.hits > 0.05) return 'Nhiều hit bị chê: tăng ngưỡng similarity của intent này.';
  if (r.hits + r.misses >= 5 && r.hits / (r.hits + r.misses) < 0.2 && r.hit_negative_feedback === 0) return 'Ít hit và chưa có hit sai: có thể giảm ngưỡng.';
  return 'Ổn định';
}

function Stat({ label, value, hint, tone, testid }: { label: string; value: string; hint?: string; tone?: 'hit' | 'danger' | 'ok'; testid?: string }) {
  const color = tone === 'hit' ? 'var(--hit)' : tone === 'danger' ? 'var(--danger)' : tone === 'ok' ? 'var(--ok)' : 'var(--ink)';
  return (
    <div className="glass rounded-[22px] p-4" data-testid={testid}>
      <div className="muted text-sm">{label}</div>
      <div className="text-[1.7rem] font-semibold leading-tight mt-1" style={{ color }} data-testid={testid ? `${testid}-value` : undefined}>{value}</div>
      {hint && <div className="faint text-xs mt-1">{hint}</div>}
    </div>
  );
}

export function Empty({ text }: { text: string }) {
  return <div className="h-full grid place-items-center faint text-sm text-center px-6">{text}</div>;
}
