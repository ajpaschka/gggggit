-- One-off cleanup: remove the RLS-verification test row inserted while
-- confirming the leads table behaves as designed (insert succeeds, public
-- read returns nothing). Not a real signup.
delete from public.leads where email = 'verify-test@example.com';
