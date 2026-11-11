import { FormEvent, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { api, ChatResponse, Citation, Me, Message, post, Session } from '../api';
import { COLLECTION_LABEL, fmtMs, StatusBadge, ThemeToggle, UserChip } from '../components/ui';

const SUGGESTIONS = [
  'Chính sách đổi trả cho phép trả hàng trong mấy ngày?',
  'Giá gói bảo hành mở rộng Vàng là bao nhiêu?',
  'Giao hàng nội thành mất bao lâu?',
  'Nhân viên được bao nhiêu ngày phép một năm?',
];

export default function ChatPage({ me }: { me: Me }) {
  const { sessionId } = useParams();
  const nav = useNavigate();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const loadSessions = () => api<Session[]>('/sessions').then(setSessions).catch(() => {});
  useEffect(() => { loadSessions(); }, []);
  useEffect(() => {
    if (!sessionId) { setMessages([]); return; }
    api<Message[]>(`/sessions/${sessionId}/messages`).then(setMessages).catch(() => nav('/chat'));
  }, [sessionId, nav]);
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, busy]);

  async function send(text: string) {
    const q = text.trim();
    if (!q || busy) return;
    setError(null);
    setInput('');
    setBusy(true);
    const tmp: Message = { id: 'tmp', role: 'user', content: q, trace_id: null, cache_status: null, citations: null, feedback: null, created_at: new Date().toISOString() };
    setMessages((m) => [...m, tmp]);
    try {
      const r = await post<ChatResponse>('/chat', { message: q, session_id: sessionId ?? null });
      const reply: Message = { id: r.message_id, role: 'assistant', content: r.answer, trace_id: r.trace_id, cache_status: r.status, citations: r.citations, feedback: null, created_at: new Date().toISOString(), latency_ms: r.latency_ms };
      setMessages((m) => [...m, reply]);
      if (!sessionId) nav(`/chat/${r.session_id}`, { replace: true });
      loadSessions();
    } catch (e: any) {
      setMessages((m) => m.filter((x) => x.id !== 'tmp' || x.content !== q));
      setInput(q);
      setError(`Chưa gửi được câu hỏi: ${e.message}. Thử gửi lại.`);
    } finally {
      setBusy(false);
    }
  }

  async function rate(m: Message, value: number) {
    const v = m.feedback === value ? 0 : value;
    await post(`/messages/${m.id}/feedback`, { value: v });
    setMessages((all) => all.map((x) => (x.id === m.id ? { ...x, feedback: v || null } : x)));
  }

  const onSubmit = (e: FormEvent) => { e.preventDefault(); send(input); };

  return (
    <div className="h-full flex gap-4 p-4 max-md:flex-col">
      <aside className="glass rounded-[28px] w-72 shrink-0 flex flex-col p-4 max-md:w-full max-md:max-h-56">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="font-semibold text-lg leading-tight">Sao Mai Helpdesk</div>
            <div className="faint text-xs">Trợ lý tra cứu tài liệu nội bộ</div>
          </div>
        </div>
        <Link to="/chat" className="pill pill-primary justify-center mb-3" data-testid="new-chat">Cuộc trò chuyện mới</Link>
        <nav className="flex-1 overflow-y-auto -mx-1" aria-label="Lịch sử trò chuyện">
          {sessions.length === 0 && <p className="faint text-sm px-2">Các cuộc trò chuyện của bạn sẽ hiện ở đây.</p>}
          {sessions.map((s) => (
            <Link key={s.id} to={`/chat/${s.id}`}
              className={`block rounded-2xl px-3 py-2 text-sm ellipsis ${s.id === sessionId ? 'glass-strong font-semibold' : 'muted hover:bg-white/30'}`}>
              {s.title}
            </Link>
          ))}
        </nav>
        <div className="pt-3 mt-3 border-t hairline text-xs">
          <div className="faint mb-1">Bạn được đọc tài liệu:</div>
          <div className="flex flex-wrap gap-1" data-testid="my-collections">
            {me.collections.map((c) => <span key={c} className="badge muted" style={{ borderColor: 'var(--line)' }}>{COLLECTION_LABEL[c] ?? c}</span>)}
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0 flex flex-col glass rounded-[28px]">
        <header className="flex items-center justify-between gap-3 px-6 py-3 border-b hairline">
          <div className="faint text-sm">Câu trả lời chỉ dựa trên tài liệu bạn được phép xem.</div>
          <div className="flex items-center gap-2">
            {me.is_console && <Link to="/console" className="pill">Mở Console</Link>}
            <ThemeToggle />
            <UserChip name={me.name} username={me.username} />
          </div>
        </header>

        <section className="flex-1 overflow-y-auto px-6 py-6" aria-live="polite">
          <div className="max-w-[72ch] mx-auto flex flex-col gap-5">
            {messages.length === 0 && !busy && (
              <div className="pt-10">
                <h1 className="text-[2rem] font-semibold leading-tight tracking-tight">Chào {me.name || me.username}, bạn cần tra cứu gì?</h1>
                <p className="muted mt-2">Hỏi về chính sách, quy trình hay quy định nội bộ. Câu hỏi giống nhau sẽ được trả lời ngay từ bộ nhớ đệm.</p>
                <div className="flex flex-wrap gap-2 mt-6">
                  {SUGGESTIONS.map((s) => <button key={s} className="pill text-sm" onClick={() => send(s)}>{s}</button>)}
                </div>
              </div>
            )}
            {messages.map((m) => m.role === 'user'
              ? <div key={m.id + m.created_at} className="self-end max-w-[85%] rounded-[22px] rounded-br-md px-4 py-2.5 pill-primary" data-testid="user-message">{m.content}</div>
              : <AssistantMessage key={m.id} m={m} onRate={rate} />)}
            {busy && <div className="faint text-sm" data-testid="thinking">Đang tra cứu tài liệu…</div>}
            <div ref={endRef} />
          </div>
        </section>

        <form onSubmit={onSubmit} className="px-6 pb-5">
          {error && <p className="text-sm mb-2" style={{ color: 'var(--danger)' }} role="alert">{error}</p>}
          <div className="max-w-[72ch] mx-auto glass glass-strong rounded-full flex items-center gap-2 pl-5 pr-1.5 py-1.5">
            <label htmlFor="q" className="sr-only">Câu hỏi</label>
            <input id="q" data-testid="chat-input" value={input} onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập câu hỏi, ví dụ: khách VIP được đổi trả trong bao lâu?" autoComplete="off"
              className="flex-1 bg-transparent outline-none py-2 min-w-0" disabled={busy} />
            <button className="pill pill-primary" type="submit" disabled={busy || !input.trim()} data-testid="send">Gửi</button>
          </div>
        </form>
      </main>
    </div>
  );
}

function AssistantMessage({ m, onRate }: { m: Message; onRate: (m: Message, v: number) => void }) {
  const cites = m.citations ?? [];
  return (
    <article className="self-start max-w-full" data-testid="assistant-message">
      <div className="glass glass-strong rounded-[22px] rounded-bl-md px-5 py-3.5 answer" data-testid="answer-text">
        <AnswerText text={m.content} cites={cites} />
      </div>
      <div className="flex flex-wrap items-center gap-2 mt-2 text-xs">
        {m.cache_status && <StatusBadge status={m.cache_status} />}
        {m.latency_ms != null && <span className="faint">{fmtMs(m.latency_ms)}</span>}
        {cites.map((c) => (
          <span key={c.label} className="faint" title={c.section}>[{c.label.slice(1)}] {c.title}</span>
        ))}
        <span className="flex-1" />
        <button className={`pill !py-1 !px-2.5 text-xs ${m.feedback === 1 ? 'pill-primary' : ''}`} onClick={() => onRate(m, 1)} aria-label="Câu trả lời hữu ích" aria-pressed={m.feedback === 1}>👍</button>
        <button className={`pill !py-1 !px-2.5 text-xs ${m.feedback === -1 ? 'pill-primary' : ''}`} onClick={() => onRate(m, -1)} aria-label="Câu trả lời sai hoặc không đúng câu hỏi" aria-pressed={m.feedback === -1} data-testid="thumbs-down">👎</button>
      </div>
    </article>
  );
}

function AnswerText({ text, cites }: { text: string; cites: Citation[] }) {
  const map = new Map(cites.map((c) => [c.label, c]));
  const parts = text.split(/(\[c\d+\])/g);
  return (
    <p className="whitespace-pre-wrap">
      {parts.map((p, i) => {
        const m = p.match(/^\[(c\d+)\]$/);
        if (!m) return <span key={i}>{p}</span>;
        const c = map.get(m[1]);
        return <sup key={i} className="cite" title={c ? `${c.title} — ${c.section}` : ''}>{m[1].slice(1)}</sup>;
      })}
    </p>
  );
}
