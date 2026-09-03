-- One-off cleanup: remove the RLS-verification test row.
delete from public.submissions where repo_url = 'https://github.com/verify-test/repo';
