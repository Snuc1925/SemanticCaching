# 09_metrics: Console: GET /api/console/metrics/overview

29 lời gọi hàm.

```text
▶ auth.current_user   [1.0 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  request = <Request>
│  ▶ auth.decode   [0.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │    in  token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiZGU1ODRiZGQtOTA3OS00NTQ1LTkwZWQtZmE1MGNjYjAyNzA3Iiwi…(+1219 ký tự)'
│  │    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ auth.console_user   [0.0 ms]   (thread: AnyIO worker thread, dòng 42)
│    in  user = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ main.console_overview   [33.8 ms]   (thread: AnyIO worker thread, dòng 152)
│    in  minutes = 1440
│    in  _ = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│  ▶ metrics.overview   [33.7 ms]   (thread: AnyIO worker thread, dòng 8)
│  │    in  minutes = 1440
│  │  ▶ db.fetch_one   [8.4 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │    in  sql = "⏎        SELECT count(*) AS requests,⏎               count(*) FILTER (WHERE status='HIT')  AS hits,⏎               count(*) FILTER (WHERE status='MISS') AS misses,⏎               count(*) FILTER (WHERE status='BYPASS') A…(+803 ký tự)"
│  │  │    in  params = {m: 1440}
│  │  │    out = {requests: 29, hits: 6, misses: 18, bypass: 1, no_cache: 4, errors: 0, llm_tokens: 16216, saved_tokens: 4505, cost_usd: 0.0019, saved_cost_usd: 0.0005, …(+4 khoá)}
│  │  ▶ db.fetch_all   [7.0 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │    in  sql = '⏎        SELECT status, count(*) AS n,⏎               percentile_cont(0.5)  WITHIN GROUP (ORDER BY latency_ms) AS p50,⏎               percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95⏎        FROM traces WH…(+104 ký tự)'
│  │  │    in  params = {m: 1440}
│  │  │    out = [{status: 'BYPASS', n: 1, p50: 1307.8, p95: 1307.8}, {status: 'HIT', n: 6, p50: 163, p95: 1045.05}, {status: 'MISS', n: 18, p50: 1811.5, p95: 5782.685}, {status: 'NO_CACHE', n: 4, p50: 1419.85, p95: 1759.55}]
│  │  ▶ db.fetch_all   [5.2 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │    in  sql = "⏎        SELECT date_trunc('minute', created_at) AS t,⏎               count(*) AS requests,⏎               count(*) FILTER (WHERE status='HIT') AS hits,⏎               count(*) FILTER (WHERE status='MISS') AS misses,⏎   …(+148 ký tự)"
│  │  │    in  params = {m: 1440}
│  │  │    out = [{t: <datetime>, requests: 3, hits: 1, misses: 2, avg_latency: 1859.4333}, {t: <datetime>, requests: 8, hits: 2, misses: 4, avg_latency: 1346.05}, {t: <datetime>, requests: 6, hits: 1, misses: 4, avg_latency: 2307.1167}, {t: <datetime>, requests: 6, hits: 1, misses: 4, avg_latency: 1497.8}, {t: <datetime>, requests: 6, hits: 1, misses: 4, avg_latency: 3169.4333}]
│  │  ▶ db.fetch_all   [5.0 ms]   (thread: AnyIO worker thread, dòng 99)
│  │  │    in  sql = "⏎        SELECT coalesce(intent,'-') AS intent, count(*) AS requests,⏎               count(*) FILTER (WHERE status='HIT') AS hits,⏎               count(*) FILTER (WHERE status='MISS') AS misses,⏎               count(*) F…(+260 ký tự)"
│  │  │    in  params = {m: 1440}
│  │  │    out = [{intent: 'return_policy', requests: 24, hits: 6, misses: 18, hit_negative_feedback: 0, avg_hit_similarity: 0.8576}, {intent: 'shipping', requests: 5, hits: 0, misses: 0, hit_negative_feedback: 0, avg_hit_similarity: None}]
│  │  ▶ cache.stats   [2.2 ms]   (thread: AnyIO worker thread, dòng 261)
│  │  │    out = {invalidated_doc_update: 4, entries: 0}
│  │  ▶ access.partitions   [1.1 ms]   (thread: AnyIO worker thread, dòng 71)
│  │  │    out = {1fb84ec24c927b56: ['cskh1'], 3963a48f4b463545: ['khach']}
│  │  ▶ metrics.revocation_stats   [4.2 ms]   (thread: AnyIO worker thread, dòng 63)
│  │  │  ▶ db.fetch_one   [4.2 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │    in  sql = '⏎        SELECT count(*) AS n,⏎               avg(extract(epoch FROM effective_at - occurred_at)) AS avg_s,⏎               max(extract(epoch FROM effective_at - occurred_at)) AS max_s⏎        FROM security_events WHERE k…(+52 ký tự)'
│  │  │  │    in  params = ()
│  │  │  │    out = {n: 7, avg_s: <Decimal>, max_s: <Decimal>}
│  │  │    out = {n: 7, avg_s: <Decimal>, max_s: <Decimal>}
│  │    out = {window_minutes: 1440, totals: {requests: 29, hits: 6, misses: 18, bypass: 1, no_cache: 4, errors: 0, llm_tokens: 16216, saved_tokens: 4505, cost_usd: 0.0019, saved_cost_usd: 0.0005, …(+4 khoá)}, hit_rate: 0.25, false_hit_rate_feedback: None, latency: {BYPASS: {n: 1, p50: 1307.8, p95: 1307.8}, HIT: {n: 6, p50: 163, p95: 1045.05}, MISS: {n: 18, p50: 1811.5, p95: 5782.685}, NO_CACHE: {n: 4, p50: 1419.85, p95: 1759.55}}, series: [{t: '2026-11-10T19:33:00+00:00', requests: 3, hits: 1, misses: 2, avg_latency: 1859.4333}, {t: '2026-11-10T19:34:00+00:00', requests: 8, hits: 2, misses: 4, avg_latency: 1346.05}, {t: '2026-11-11T04:05:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 2307.1167}, {t: '2026-11-11T04:07:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 1497.8}, {t: '2026-11-11T04:37:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 3169.4333}], by_intent: [{intent: 'return_policy', requests: 24, hits: 6, misses: 18, hit_negative_feedback: 0, avg_hit_similarity: 0.8576}, {intent: 'shipping', requests: 5, hits: 0, misses: 0, hit_negative_feedback: 0, avg_hit_similarity: None}], cache: {invalidated_doc_update: 4, entries: 0}, partitions: {1fb84ec24c927b56: ['cskh1'], 3963a48f4b463545: ['khach']}, revocation: {n: 7, avg_s: <Decimal>, max_s: <Decimal>}}
│    out = {window_minutes: 1440, totals: {requests: 29, hits: 6, misses: 18, bypass: 1, no_cache: 4, errors: 0, llm_tokens: 16216, saved_tokens: 4505, cost_usd: 0.0019, saved_cost_usd: 0.0005, …(+4 khoá)}, hit_rate: 0.25, false_hit_rate_feedback: None, latency: {BYPASS: {n: 1, p50: 1307.8, p95: 1307.8}, HIT: {n: 6, p50: 163, p95: 1045.05}, MISS: {n: 18, p50: 1811.5, p95: 5782.685}, NO_CACHE: {n: 4, p50: 1419.85, p95: 1759.55}}, series: [{t: '2026-11-10T19:33:00+00:00', requests: 3, hits: 1, misses: 2, avg_latency: 1859.4333}, {t: '2026-11-10T19:34:00+00:00', requests: 8, hits: 2, misses: 4, avg_latency: 1346.05}, {t: '2026-11-11T04:05:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 2307.1167}, {t: '2026-11-11T04:07:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 1497.8}, {t: '2026-11-11T04:37:00+00:00', requests: 6, hits: 1, misses: 4, avg_latency: 3169.4333}], by_intent: [{intent: 'return_policy', requests: 24, hits: 6, misses: 18, hit_negative_feedback: 0, avg_hit_similarity: 0.8576}, {intent: 'shipping', requests: 5, hits: 0, misses: 0, hit_negative_feedback: 0, avg_hit_similarity: None}], cache: {invalidated_doc_update: 4, entries: 0}, partitions: {1fb84ec24c927b56: ['cskh1'], 3963a48f4b463545: ['khach']}, revocation: {n: 7, avg_s: <Decimal>, max_s: <Decimal>}}

```
