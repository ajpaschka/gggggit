-- submissions: free, public repo submissions for the library. No account,
-- no session, no payment gate -- anyone can submit, Alexander reviews and
-- decides what actually gets added to data/library.json (this table is
-- never auto-published; it's an inbox, not the library itself). Same
-- insert-only RLS shape as public.leads: anon can insert, nobody --
-- including a signed-in visitor -- can read the list back through the
-- public API. Reviewed via Supabase Studio -> Table Editor.

create table public.submissions (
  id uuid primary key default gen_random_uuid(),
  repo_url text not null,
  note text,
  submitter_email text,
  status text not null default 'new',
  created_at timestamptz not null default now()
);

alter table public.submissions enable row level security;

create policy "anyone can submit a repo"
  on public.submissions for insert
  to anon
  with check (true);
