// notify-submission — Supabase Edge Function
//
// Fires on every INSERT into public.submissions (wired via a Database
// Webhook — see supabase/functions/notify-submission/SETUP.md for the
// one manual dashboard step, since a webhook can't be created from a
// committed migration without embedding a live secret in git). Sends
// Alexander one email per submission via Resend so a new repo suggestion
// actually reaches him instead of sitting silently in a table only
// visible via Supabase Studio's Table Editor.
//
// This function does NOT touch data/library.json or decide anything —
// it only notifies. Alexander still reviews every submission by hand
// and decides what (if anything) gets added; see append-entries.py for
// the only thing allowed to write the library itself. Added 2026-09-04,
// decision recorded in AJAI's agora/echo-log.md same date: the nightly
// GitHub Trending Scan auto-publish stays ungated (risk accepted), but
// human-submitted entries get this review path instead.

const RESEND_API_KEY = Deno.env.get("RESEND_API_KEY");
const NOTIFY_TO = Deno.env.get("NOTIFY_EMAIL") ?? "ajpaschka@gmail.com";
// Resend's shared test domain — works with zero setup, no domain
// verification needed. Swap for a verified domain address later if
// deliverability to Gmail's inbox (not spam) ever becomes an issue.
const FROM_ADDRESS = "GGGGGIT! <onboarding@resend.dev>";

function escapeHtml(s: string): string {
  return s.replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c] as string
  ));
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response("method not allowed", { status: 405 });
  }
  if (!RESEND_API_KEY) {
    console.error("RESEND_API_KEY not set — see SETUP.md");
    return new Response("not configured", { status: 500 });
  }

  let payload: any;
  try {
    payload = await req.json();
  } catch {
    return new Response("bad json", { status: 400 });
  }

  // Supabase Database Webhook payload shape:
  // { type: "INSERT", table: "submissions", schema: "public", record: {...}, old_record: null }
  if (payload?.type !== "INSERT" || payload?.table !== "submissions") {
    return new Response("ignored: not a submissions insert", { status: 200 });
  }

  const row = payload.record ?? {};
  const repoUrl = String(row.repo_url ?? "(missing)");
  const note = row.note ? String(row.note) : null;
  const submitterEmail = row.submitter_email ? String(row.submitter_email) : null;
  const createdAt = row.created_at ?? new Date().toISOString();

  const subject = `gggggit submission: ${repoUrl}`;
  const html = `
    <p><strong>New repo submission</strong> — ${escapeHtml(createdAt)}</p>
    <p><a href="${escapeHtml(repoUrl)}">${escapeHtml(repoUrl)}</a></p>
    ${note ? `<p><em>Why it's worth including:</em> ${escapeHtml(note)}</p>` : ""}
    ${submitterEmail ? `<p>Submitter: ${escapeHtml(submitterEmail)}</p>` : ""}
    <p style="color:#888;font-size:12px">Review in Supabase Studio → Table Editor → submissions.
    This email is a notification only — nothing auto-publishes to the library.</p>
  `;

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: FROM_ADDRESS,
      to: [NOTIFY_TO],
      subject,
      html,
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    console.error("resend send failed", res.status, errText);
    return new Response("email send failed", { status: 502 });
  }

  return new Response("ok", { status: 200 });
});
