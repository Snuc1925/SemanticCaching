import { useEffect, useRef } from 'react';
import { API } from './api';
import { token } from './auth';

type Handler = (type: string, data: any) => void;

/** Nghe sự kiện realtime của Console (SSE). EventSource không gửi được header nên token đi qua query. */
export function useConsoleStream(onEvent: Handler) {
  const ref = useRef(onEvent);
  ref.current = onEvent;
  useEffect(() => {
    let es: EventSource | null = null;
    let closed = false;
    (async () => {
      const t = await token();
      if (closed) return;
      es = new EventSource(`${API}/api/console/stream?token=${encodeURIComponent(t)}`);
      for (const type of ['trace', 'audit', 'security']) {
        es.addEventListener(type, (e) => ref.current(type, JSON.parse((e as MessageEvent).data)));
      }
    })();
    return () => {
      closed = true;
      es?.close();
    };
  }, []);
}
