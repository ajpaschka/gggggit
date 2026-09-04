# GGGGGIT!

A tagged, permanent library of real, trending GitHub repos — not a feed that churns and vanishes.
Named as a riff on [FFFFOUND!](https://en.wikipedia.org/wiki/FFFFOUND!)'s repeated-letter
convention; built in the spirit of [We Are Hunted](https://en.wikipedia.org/wiki/We_Are_Hunted)'s
tile-based, "digestible in three seconds" discovery model — but structured as a browsable library,
not an ephemeral daily feed.

Every entry is real: found by a script that actually queries GitHub's public Search API, never
invented or padded. If nothing relevant turns up in a given week, nothing gets added that week —
no filler.

## How it works

- `data/library.json` — the entire library. Tags, colors, and every entry, forever.
- `index.html` — a static page that fetches `data/library.json` and renders it as a tag-filterable
  grid of Pantone-chip-style cards. No backend, no database, no build step.
- `scripts/` — the update pipeline that appends new entries weekly (see below).

## Community submissions

The site's submit-a-repo form writes into `public.submissions` (Supabase, insert-only —
nobody can read the list back through the public API). A Database Webhook fires
`supabase/functions/notify-submission/` on every insert, which emails Alexander so a
submission actually surfaces instead of waiting to be noticed in Supabase Studio. Nothing
here auto-publishes — every submission is reviewed by hand before (if ever) becoming a real
`append-entries.py` entry. See `supabase/functions/notify-submission/SETUP.md` for the two
one-time setup steps (a Resend API key, a Dashboard webhook click).

**This is deliberately the only reviewed path into the library.** The nightly automated
scan (`scripts/append-entries.py`, run by a Hermes cron job) publishes straight to
`data/library.json` and pushes live with no human review step — Alexander decided
2026-09-04 to accept that risk for scan-sourced entries specifically (real GitHub data,
topic-filtered, lower stakes than a public-facing factual claim) rather than review 15-20
scan candidates a night. Human-submitted entries get the opposite treatment, since they
come from strangers and carry a different risk (spam, off-topic, or worse) that the scan's
own topic pre-filtering doesn't apply to. See AJAI's `agora/echo-log.md`, 2026-09-04, for
the full reasoning.

## Local preview

```
python3 -m http.server 8000
```

`fetch()` needs a real server — opening `index.html` directly via `file://` won't load the data.

## Tags

Six categories, grounded in what real scans have actually turned up (not designed in the abstract):
AI & Agents, Design & Visual Tools, Data Visualization, Creative Coding, Video & Motion, Agent
Practice. New tags only get added when real content justifies them, same as Agent Practice did.

## Color sequence

Each entry gets the next color in a considered ROYGBIV sequence (not primary-crayon hues — see
the hex values in `data/library.json`'s `colors` array). When the sequence laps back around, a
different real value from that hue family gets used instead of an exact repeat — never quite the
same color twice.

Built by [Alexander Paschka](https://paschkastudio.com).
