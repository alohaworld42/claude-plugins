#!/usr/bin/env python3
"""Search past session digests and print ranked hits with context.

Keyword scoring over the local store. Prints digest paths so the agent can
Read only the ones that matter instead of loading the whole history —
that is where the token saving comes from.
"""

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_STORE = Path(os.environ.get("WRAPUP_STORE", Path.home() / ".claude" / "wrapup"))


def score(text_lower: str, terms: list[str]) -> tuple[int, int]:
    """(number of distinct terms matched, total hits) — distinct wins first."""
    hits = [len(re.findall(re.escape(t), text_lower)) for t in terms]
    return sum(1 for h in hits if h), sum(hits)


def main() -> int:
    p = argparse.ArgumentParser(description="Search past session digests.")
    p.add_argument("query", nargs="+", help="Search terms (all lowercased)")
    p.add_argument("--store", default=str(DEFAULT_STORE))
    p.add_argument("--limit", type=int, default=5, help="Max digests to report")
    p.add_argument("--context", type=int, default=2, help="Matching lines per digest")
    p.add_argument("--project", default="", help="Only digests with this project")
    args = p.parse_args()

    sessions = Path(args.store) / "sessions"
    if not sessions.is_dir():
        print(f"no store yet at {sessions} — nothing recalled")
        return 0

    terms = [t.lower() for t in args.query]
    results = []
    for path in sessions.glob("*.md"):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        low = text.lower()
        if args.project and f"project: {args.project.lower()}" not in low:
            continue
        distinct, total = score(low, terms)
        if distinct:
            results.append((distinct, total, path, text))

    if not results:
        print(f"no digests matched: {' '.join(terms)}")
        return 0

    results.sort(key=lambda r: (r[0], r[1], r[2].name), reverse=True)
    print(f"{len(results)} digest(s) matched — showing top {min(args.limit, len(results))}\n")
    for distinct, total, path, text in results[:args.limit]:
        title = next((l[7:].strip() for l in text.splitlines() if l.startswith("title: ")), path.stem)
        print(f"## {title}")
        print(f"   {path}  ({distinct}/{len(terms)} terms, {total} hits)")
        shown = 0
        for line in text.splitlines():
            if shown >= args.context:
                break
            low = line.lower()
            if any(t in low for t in terms) and not line.startswith(("title:", "tags:", "---")):
                print(f"   > {line.strip()[:160]}")
                shown += 1
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
