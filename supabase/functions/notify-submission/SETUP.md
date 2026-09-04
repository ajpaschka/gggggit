# Setting up submission email notifications

Two manual steps — one is a real account/API-key you have to create, the other is a
one-click dashboard wire-up. Neither can be done from a committed file: the API key is a
secret (never belongs in git), and the webhook needs the function's live deployed URL,
which doesn't exist until after deploy. Same shape as `oauth-setup`'s "one manual step
per provider that cannot be automated."

## 1 — Deploy the function

```bash
cd gggggit-site
supabase functions deploy notify-submission
```

## 2 — Get a Resend API key (free tier: 3,000 emails/month, no credit card)

1. Sign up at resend.com with the email you want notifications to land in (or any email —
   the *sending* account doesn't have to match the *receiving* address).
2. Dashboard → API Keys → Create API Key. Copy it — shown once.
3. Push it as a function secret (never written to any file):

```bash
supabase secrets set RESEND_API_KEY="re_your_real_key_here"
```

The function defaults to notifying `ajpaschka@gmail.com`. To change the destination without
touching code:

```bash
supabase secrets set NOTIFY_EMAIL="some-other-address@example.com"
```

**Deliverability note:** the function sends from `onboarding@resend.dev`, Resend's shared
test domain — works immediately, zero setup, but mail from a shared domain sometimes lands
in spam on the first few sends. If that happens, verify your own domain in Resend's
dashboard (a few DNS records) and swap `FROM_ADDRESS` in `index.ts` for an address on it —
not required to get this working, just improves inbox placement long-term.

## 3 — Wire the Database Webhook (the one dashboard-only step)

Supabase Dashboard → Database → Webhooks → Create a new webhook:

| Field | Value |
|---|---|
| Name | `notify-submission` |
| Table | `public.submissions` |
| Events | `Insert` only |
| Type | Edge Function |
| Edge Function | `notify-submission` |

The dashboard wires the auth header itself (the deployed function requires a valid Supabase
JWT by default, and a Dashboard-created webhook already sends one) — nothing else to
configure. This step isn't scripted into a migration on purpose: doing so would mean
either committing a live secret to git, or shipping a webhook trigger that silently does
nothing until someone notices — a five-minute dashboard click is more honest than either.

## Verify it actually works

Submit a real (or throwaway) repo URL through the site's own form, then confirm an email
actually lands — don't call this done from reading the code. If nothing arrives:

- Check Supabase Dashboard → Edge Functions → notify-submission → Logs for an error.
- Confirm `RESEND_API_KEY` is set: `supabase secrets list`.
- Confirm the webhook fired at all: Database → Webhooks → notify-submission → should show
  a recent delivery attempt with its response status.
