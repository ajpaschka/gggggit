#!/usr/bin/env python3
"""append-entries.py — the only thing allowed to write to data/library.json.

Takes a JSON file of candidate entries (produced by an agent that already
decided which real repos are library-worthy and picked their tag/description)
and merges genuinely new ones into the library. All the parts that must not
be gotten wrong live here, in deterministic code, not left to an LLM to
hand-edit JSON correctly on the fly:

  - Dedup by `repo` (case-insensitive) against every entry already in the
    library, not just the current run's batch.
  - Sequence numbers assigned from `next_seq`, incremented one at a time —
    never trust a candidate-supplied seq.
  - Tag slugs validated against the library's own tag list; an unknown tag
    is a hard error, not silently accepted (a typo'd tag would otherwise
    vanish from the site's filter nav with no warning).

Usage:
    python3 append-entries.py candidates.json
    python3 append-entries.py candidates.json --dry-run   # report only, no write

candidates.json shape:
[
  {
    "repo": "owner/name",
    "name": "display-name",
    "url": "https://github.com/owner/name",
    "description": "One precise, factual sentence on what it does.",
    "tags": ["creative-coding"],
    "stars": 42,
    "date_found": "2026-09-07"
  },
  ...
]
"""

import json
import sys
from pathlib import Path

LIBRARY_PATH = Path(__file__).resolve().parent.parent / "data" / "library.json"

REQUIRED_FIELDS = {"repo", "name", "url", "description", "tags", "stars", "date_found"}


def load_library():
    with open(LIBRARY_PATH) as f:
        return json.load(f)


def main():
    if len(sys.argv) < 2:
        print("Usage: append-entries.py candidates.json [--dry-run]", file=sys.stderr)
        sys.exit(1)

    candidates_path = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    with open(candidates_path) as f:
        candidates = json.load(f)

    if not isinstance(candidates, list):
        print("candidates.json must be a JSON array", file=sys.stderr)
        sys.exit(1)

    library = load_library()
    valid_tags = {t["slug"] for t in library["tags"]}
    existing_repos = {e["repo"].lower() for e in library["entries"]}

    added = []
    skipped_dupe = []
    errors = []

    for i, c in enumerate(candidates):
        # A malformed candidate is skipped and reported, not a reason to
        # block every other, valid candidate in the same weekly batch —
        # this runs unattended, so one bad entry can't be allowed to
        # silently withhold everything real that week.
        missing = REQUIRED_FIELDS - c.keys()
        if missing:
            errors.append(f"candidate #{i} ({c.get('repo', '?')}): missing fields {missing}")
            continue

        bad_tags = set(c["tags"]) - valid_tags
        if bad_tags:
            errors.append(
                f"candidate #{i} ({c['repo']}): unknown tag(s) {bad_tags} — "
                f"valid tags are {sorted(valid_tags)}"
            )
            continue

        if c["repo"].lower() in existing_repos:
            skipped_dupe.append(c["repo"])
            continue

        entry = {
            "id": f"{c['name']}-{c['date_found'].replace('-', '')}",
            "repo": c["repo"],
            "name": c["name"],
            "url": c["url"],
            "description": c["description"],
            "tags": c["tags"],
            "stars": c["stars"],
            "date_found": c["date_found"],
            "seq": library["next_seq"],
        }
        library["entries"].append(entry)
        existing_repos.add(c["repo"].lower())  # guard against dupes within the same batch too
        library["next_seq"] += 1
        added.append(entry)

    if errors:
        print("ERRORS — these candidates were skipped, everything else still processed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)

    print(f"Added: {len(added)}")
    for e in added:
        print(f"  SIGNAL {e['seq']:02d} — {e['name']} ({e['repo']}) [{', '.join(e['tags'])}]")
    print(f"Skipped (already in library): {len(skipped_dupe)}")
    for r in skipped_dupe:
        print(f"  - {r}")

    if dry_run:
        print("\n--dry-run: not written.")
        sys.exit(1 if errors else 0)

    if not added:
        print("\nNothing new — library.json not touched.")
        sys.exit(1 if errors else 0)

    with open(LIBRARY_PATH, "w") as f:
        json.dump(library, f, indent=2)
        f.write("\n")
    print(f"\nWrote {LIBRARY_PATH}")
    # Non-zero exit when there were errors (even though valid entries were
    # still written) so the cron log surfaces it for a later look — but the
    # write itself already happened, nothing good was held back.
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
