-- Bug found 2026-09-04: a signed-in visitor (heart feature uses GitHub OAuth)
-- got "new row violates row-level security policy" submitting a repo. The
-- original policy only granted INSERT to `anon` -- once someone is signed
-- in, supabase-js sends every request as `authenticated` instead, which had
-- no matching policy at all. Real repro: Alexander signed in, tried to
-- submit, got exactly this error; a logged-out curl test with the raw anon
-- key always succeeded, which is why this took a few rounds to actually
-- find. See agora/echo-log.md, 2026-09-04, for the full debugging trail.
drop policy "anyone can submit a repo" on public.submissions;

create policy "anyone can submit a repo"
  on public.submissions for insert
  to anon, authenticated
  with check (true);
