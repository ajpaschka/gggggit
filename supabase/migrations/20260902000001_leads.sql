-- leads: email captures for the footer "notify me about new additions"
-- signup (and any future gated resource on this site). No account, no
-- session — the whole point is zero-friction. RLS allows insert-only from
-- the public anon key; the list itself is never readable through the
-- public API, only via Supabase Studio or a service-role script.
--
-- Consent note: this form's only purpose is the notification itself
-- (there's no separate download/resource riding alongside it), so
-- submitting it IS the specific, informed, affirmative act — no extra
-- checkbox needed. marketing_consent is still recorded explicitly rather
-- than assumed, so the record is self-explaining without needing this
-- comment to be re-read later.

create table public.leads (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  resource text not null default 'weekly-digest',
  marketing_consent boolean not null default false,
  marketing_consent_at timestamptz,
  created_at timestamptz not null default now()
);

alter table public.leads enable row level security;

create policy "anyone can submit a lead"
  on public.leads for insert
  to anon
  with check (true);
