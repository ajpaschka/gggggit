-- One-off cleanup: remove debug rows inserted while diagnosing a transient
-- PostgREST schema-cache staleness on public.submissions right after the
-- Database Webhooks integration was installed (see agora/echo-log.md,
-- 2026-09-04 — root cause confirmed, not a real RLS bug).
delete from public.submissions where repo_url in (
  'https://github.com/test/debug-reproduce',
  'https://github.com/test/debug-reproduce-2',
  'https://github.com/test/debug-with-note',
  'https://github.com/test/debug-reproduce-3'
);
delete from public.leads where email = 'debug-test@example.com' and resource = 'debug-test';
