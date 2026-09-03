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
