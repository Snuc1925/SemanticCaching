import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api, Span, TraceDetail } from '../../api';
import { COLLECTION_LABEL, fmtMs, fmtTime, fmtUsd, StatusBadge } from '../../components/ui';
import { useConsoleStream } from '../../stream';
import { Panel } from './Layout';

/** Trang chi tiết: pipeline là một "đường ray" dọc; bước quyết định HIT/MISS được làm nổi bật. */
export default function RequestDetail() {
  const { id } = useParams();
  const [t, setT] = useState<TraceDetail | null>(null);
  const [err, setErr] = useState<string | null>(null);
  useEffect(() => { api<TraceDetail>(`/console/traces/${id}`).then(setT).catch((e) => setErr(e.message)); }, [id]);
  useConsoleStream((type, d) => { if (type === 'audit' && d.id === id) setT((x) => (x ? { ...x, unauthorized: d.unauthorized, audit: d.audit } : x)); });

  if (err) return <Panel><p>Không tải được request: {err}</p><Link className="pill mt-3" to="/console/requests">Quay lại danh sách</Link></Panel>;
  if (!t) return <p className="muted p-4">Đang tải…</p>;
  const total = Math.max(t.latency_ms ?? 1, 1);

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
      <Panel>
        <Link to="/console/requests" className="faint text-sm">‹ Danh sách request</Link>
        <h1 className="text-[1.6rem] font-semibold leading-snug mt-2" data-testid="trace-question">{t.question}</h1>
        <div className="flex flex-wrap items-center gap-3 mt-2 text-sm">
          <StatusBadge status={t.status} />
          <span className="muted">{t.username}, lúc {fmtTime(t.created_at)}</span>
          <span className="muted">tổng {fmtMs(t.latency_ms)}</span>
        </div>

        <ol className="mt-6 relative" data-testid="trace-timeline">
          <span className="absolute left-[11px] top-2 bottom-2 w-[2px]" style={{ background: 'var(--line)' }} aria-hidden />
          {t.spans.map((s, i) => {
            const decisive = s.name === 'cache_lookup' || s.name === 'cache_hit';
            const color = s.status === 'error' ? 'var(--danger)' : decisive ? (t.status === 'HIT' ? 'var(--hit)' : 'var(--miss)') : 'var(--ink-faint)';
            return (
              <li key={i} className="relative pl-10 pb-5" data-testid={`span-${s.name}`}>
                <span className="absolute left-0 top-1 w-6 h-6 rounded-full glass grid place-items-center" style={{ borderColor: color }}>
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: color }} />
                </span>
                <div className={`rounded-2xl ${decisive ? 'glass p-4' : ''}`} style={decisive ? { borderColor: color } : undefined}>
                  <div className="flex items-baseline gap-3 flex-wrap">
                    <h3 className="font-semibold">{s.title}</h3>
                    <span className="faint text-xs">{fmtMs(s.duration_ms)}</span>
                    <span className="flex-1 min-w-12 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--line)' }} aria-hidden>
                      <span className="block h-full rounded-full" style={{ marginLeft: `${(s.start_ms / total) * 100}%`, width: `${Math.max((s.duration_ms / total) * 100, 1)}%`, background: color }} />
                    </span>
                  </div>
                  <SpanBody s={s} />
                </div>
              </li>
            );
          })}
        </ol>
      </Panel>

      <div className="grid gap-4 content-start">
        <Panel title="Chi phí">
          <dl className="grid grid-cols-2 gap-y-1 text-sm">
            <dt className="muted">Token LLM vào</dt><dd>{t.llm_tokens_in}</dd>
            <dt className="muted">Token LLM ra</dt><dd>{t.llm_tokens_out}</dd>
            <dt className="muted">Token embedding</dt><dd>{t.embed_tokens}</dd>
            <dt className="muted">Chi phí</dt><dd>{fmtUsd(t.cost_usd)}</dd>
            <dt className="muted">Tiết kiệm nhờ cache</dt><dd style={{ color: t.saved_tokens ? 'var(--hit)' : undefined }}>{t.saved_tokens ? `${t.saved_tokens} token, ${fmtUsd(t.saved_cost_usd)}` : '–'}</dd>
          </dl>
        </Panel>
        <Panel title="Audit rò rỉ (canary)">
          {t.audit == null ? <p className="faint text-sm">Đang kiểm tra…</p> : (
            <div className="text-sm" data-testid="audit">
              <p style={{ color: t.unauthorized ? 'var(--danger)' : 'var(--ok)' }} className="font-semibold">
                {t.unauthorized ? 'Câu trả lời chứa thông tin vượt quyền' : 'Không phát hiện thông tin vượt quyền'}
              </p>
              <p className="muted mt-1">
                {t.audit.canaries.length === 0 ? 'Không có giá trị canary nào trong câu trả lời.'
                  : `Canary tìm thấy: ${t.audit.canaries.map((c: any) => `${c.id} (${COLLECTION_LABEL[c.collection] ?? c.collection})`).join(', ')}. IAM xác nhận user ${t.audit.denied_collections.length ? 'KHÔNG có quyền: ' + t.audit.denied_collections.join(', ') : 'có quyền đọc các collection này'}.`}
              </p>
            </div>
          )}
        </Panel>
        <Panel title="Partition">
          <p className="text-sm break-all">{t.partition ?? '–'}</p>
          <p className="faint text-xs mt-1">Mã hash của tập collection người hỏi được đọc. Chỉ user có cùng mã mới dùng chung cache.</p>
        </Panel>
      </div>
    </div>
  );
}

function KV({ k, v }: { k: string; v: React.ReactNode }) {
  return <div className="flex gap-2 text-sm"><span className="muted shrink-0 w-40">{k}</span><span className="min-w-0 break-words">{v}</span></div>;
}

function SpanBody({ s }: { s: Span }) {
  const d = s.data;
  if (d.error) return <p className="text-sm mt-1" style={{ color: 'var(--danger)' }}>{d.error}</p>;
  switch (s.name) {
    case 'identity':
      return <div className="mt-1 grid gap-0.5">
        <KV k="Signature" v={<>{d.signature} <span className="faint">({d.signature_from_cache ? 'lấy từ cache' : 'vừa tính lại từ IAM'})</span></>} />
        <KV k="Collection được đọc" v={(d.collections as string[]).map((c) => COLLECTION_LABEL[c] ?? c).join(', ')} />
      </div>;
    case 'embed':
      return <div className="mt-1"><KV k="Model" v={`${d.model}${d.from_cache ? ' (vector lấy từ cache embedding)' : `, ${d.tokens} token`}`} /></div>;
    case 'classify':
      return <div className="mt-1 grid gap-0.5">
        <KV k="Chính sách cache" v={<><b>{d.policy}</b> <span className="muted">— {d.reason}</span></>} />
        <KV k="Intent" v={`${d.intent} (độ gần ${d.intent_similarity})`} />
        <KV k="Entity" v={Object.keys(d.entities ?? {}).length ? JSON.stringify(d.entities) : 'không có'} />
      </div>;
    case 'cache_lookup':
      return <div className="mt-2">
        <KV k="Ngưỡng similarity" v={d.threshold} />
        {d.signature_invalidated && <KV k="Lưu ý" v="IAM từ chối khi kiểm lại, signature đã bị xoá để tính lại" />}
        <table className="data mt-2" data-testid="candidates">
          <thead><tr><th>Entry ứng viên</th><th>Similarity</th><th>Kết luận</th></tr></thead>
          <tbody>
            {(d.candidates ?? []).length === 0 && <tr><td colSpan={3} className="faint">Partition này chưa có entry nào.</td></tr>}
            {(d.candidates ?? []).map((c: any) => (
              <tr key={c.entry_id}>
                <td>{c.question}</td>
                <td>{Number(c.similarity).toFixed(3)}</td>
                <td style={{ color: c.passed ? 'var(--hit)' : undefined }}>{c.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>;
    case 'cache_hit':
      return <div className="mt-1 grid gap-0.5">
        <KV k="Câu hỏi gốc trong cache" v={d.cached_question} />
        <KV k="Số lần đã dùng lại" v={d.hits} />
        <KV k="Nguồn (provenance)" v={[...new Set((d.provenance ?? []).map((p: any) => `${p.doc_id} v${p.version}`))].join(', ')} />
        <KV k="Tiết kiệm" v={`${d.saved_tokens} token`} />
      </div>;
    case 'retrieval':
      return <div className="mt-2">
        <KV k="Lọc trước theo" v={(d.filter_collections as string[]).map((c) => COLLECTION_LABEL[c] ?? c).join(', ')} />
        <table className="data mt-2"><thead><tr><th>Đoạn tài liệu</th><th>Collection</th><th>Score</th></tr></thead>
          <tbody>{(d.chunks ?? []).map((c: any) => (
            <tr key={c.chunk_id}><td><div className="font-medium">{c.section}</div><div className="faint text-xs">{c.preview}</div></td><td>{COLLECTION_LABEL[c.collection] ?? c.collection}</td><td>{c.score}</td></tr>
          ))}</tbody></table>
      </div>;
    case 'iam_verify':
      return <div className="mt-1 grid gap-0.5">
        <KV k="Quyết định IAM" v={Object.entries(d.decisions ?? {}).map(([c, ok]) => `${COLLECTION_LABEL[c] ?? c}: ${ok ? 'cho phép' : 'từ chối'}`).join(', ') || 'không có đoạn nào'} />
        <KV k="Đoạn bị chặn" v={(d.blocked ?? []).length || 'không'} />
      </div>;
    case 'llm':
      return d.skipped ? <p className="muted text-sm mt-1">{d.reason}</p> : <div className="mt-1 grid gap-0.5">
        <KV k="Model / prompt" v={`${d.model}, prompt ${d.prompt_version}`} />
        <KV k="Token" v={`${d.tokens_in} vào, ${d.tokens_out} ra (${fmtUsd(d.cost_usd)})`} />
      </div>;
    case 'admission':
      return <div className="mt-1 grid gap-0.5">
        <KV k="Lưu vào cache" v={<b style={{ color: d.admitted ? 'var(--hit)' : undefined }}>{d.admitted ? 'Có' : 'Không'}</b>} />
        <KV k="Lý do" v={(d.reasons ?? []).join('; ')} />
        {d.admitted && <KV k="Provenance" v={(d.provenance_docs ?? []).join(', ')} />}
      </div>;
    default:
      return <pre className="text-xs mt-1 overflow-x-auto">{JSON.stringify(d, null, 2)}</pre>;
  }
}
