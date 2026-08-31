-- hearts: per-user saved entries. Explicitly separate from data/library.json,
-- which stays the single shared, public, append-only catalog exactly as it
-- already works — hearts are private per-user mutable state, a different
-- kind of data.

create table public.hearts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  repo text not null,
  created_at timestamptz not null default now(),
  unique (user_id, repo)
);

alter table public.hearts enable row level security;

-- A user can only ever see, create, or remove their OWN heart rows.
-- Nobody's individual heart list is exposed to anyone else, including
-- other authenticated users — the only public surface is the aggregate
-- view below, which exposes counts, never who-hearted-what.

create policy "users can view their own hearts"
  on public.hearts for select
  using (auth.uid() = user_id);

create policy "users can heart on their own behalf"
  on public.hearts for insert
  with check (auth.uid() = user_id);

create policy "users can unheart their own hearts"
  on public.hearts for delete
  using (auth.uid() = user_id);

-- Public heart counts, per repo. Views run with their OWNER's privileges
-- by default (security_invoker = false) rather than the querying user's —
-- that's what lets this aggregate read across every row despite the base
-- table's RLS restricting direct row access to each user's own hearts.
-- This view is the ONLY way the public heart count reaches the site;
-- individual user-to-repo mappings never leave the hearts table itself.
create view public.heart_counts
  with (security_invoker = false)
  as
  select repo, count(*)::int as hearts
  from public.hearts
  group by repo;

grant select on public.heart_counts to anon, authenticated;
