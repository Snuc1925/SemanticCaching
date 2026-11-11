import { token } from './auth';

export const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API}/api${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${await token()}`, ...(init.headers ?? {}) },
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      msg = (await res.json()).detail ?? msg;
    } catch { /* body không phải JSON */ }
    throw new ApiError(res.status, String(msg));
  }
  return res.json() as Promise<T>;
}

export const post = <T,>(path: string, body: unknown) => api<T>(path, { method: 'POST', body: JSON.stringify(body) });

// ---------- types ----------
export type CacheStatus = 'HIT' | 'MISS' | 'BYPASS' | 'NO_CACHE' | 'ERROR';

export interface Me {
  user_id: string; username: string; name: string; roles: string[];
  is_console: boolean; signature: string; collections: string[];
}
export interface Citation { label: string; doc_id: string; title: string; section: string; collection: string; version: number }
export interface ChatResponse {
  session_id: string; message_id: string; trace_id: string; status: CacheStatus; answer: string;
  citations: Citation[]; latency_ms: number; similarity: number | null; policy: string;
}
export interface Session { id: string; title: string; updated_at: string }
export interface Message {
  id: string; role: 'user' | 'assistant'; content: string; trace_id: string | null;
  cache_status: CacheStatus | null; citations: Citation[] | null; feedback: number | null; created_at: string;
  latency_ms?: number;
}
export interface TraceSummary {
  id: string; created_at: string; username: string; question: string; status: CacheStatus; policy: string;
  intent: string; partition: string; similarity: number | null; latency_ms: number;
  llm_tokens_in: number; llm_tokens_out: number; cost_usd: number; saved_tokens: number; saved_cost_usd: number;
  unauthorized: boolean | null; feedback: number | null;
}
export interface Span { name: string; title: string; start_ms: number; duration_ms: number; status: string; data: Record<string, any> }
export interface TraceDetail extends TraceSummary { spans: Span[]; audit: any; entry_id: string | null; embed_tokens: number }
export interface SecurityEvent {
  id: number; kind: string; source: string; occurred_at: string; detected_at: string; effective_at: string | null;
  summary: string; details: any; window_seconds?: number;
}
