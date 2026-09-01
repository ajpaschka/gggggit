#!/usr/bin/env python3
"""Stripped-down, copy-paste-ready link list of recent gggggit library
entries — for pasting straight into a social post (LinkedIn, Skool, etc.),
no markdown, no HTML, just name / description / bare URL.

Usage:
  python3 link-list.py                 # entries from the last 7 days
  python3 link-list.py --days 1        # just today's additions
  python3 link-list.py --days 30       # a longer lookback
"""

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
LIBRARY = HERE.parent / "data" / "library.json"
SITE_URL = "https://ajpaschka.github.io/gggggit/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="lookback window in days (default 7)")
    args = ap.parse_args()

    data = json.loads(LIBRARY.read_text())
    cutoff = (date.today() - timedelta(days=args.days - 1)).isoformat()

    recent = [e for e in data["entries"] if e["date_found"] >= cutoff]
    recent.sort(key=lambda e: e["seq"])

    if not recent:
        print(f"No entries added in the last {args.days} day(s).")
        return

    label = "today" if args.days == 1 else f"the last {args.days} days"
    lines = [f"New on gggggit — {len(recent)} find(s) from {label}:", ""]
    for e in recent:
        lines.append(f"{e['name']} — {e['description']}")
        lines.append(e["url"])
        lines.append("")
    lines.append(f"Browse the full library: {SITE_URL}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
