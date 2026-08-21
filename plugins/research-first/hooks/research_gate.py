#!/usr/bin/env python3
"""UserPromptSubmit gate for research-first.

Reads the hook payload on stdin, decides whether the prompt looks like a
question that should be grounded in sources rather than memory, and prints a
short reminder only then. Silent otherwise — a hook that fires on every prompt
gets ignored within a day.

Kill switch: create ~/.claude/research-first-off
"""

import json
import os
import re
import sys

REMINDER = """<research-first>
This prompt looks answerable from memory. Don't. Search first: 3-5 differently
worded queries (jargon / plain / verbatim error / "X limitations" / primary
source), open >=3 sources of different type, name where they agree and where
they conflict, trace load-bearing numbers to their origin, then reason. Cite
what the answer rests on. Repo-local questions: grep is the search, ignore this.
Full method: /research-first:research-first
</research-first>"""

# Things that change, or that a human would google before claiming.
SIGNALS = [
    r"\bversion(s|en)?\b", r"\brelease[ds]?\b", r"\bchangelog\b", r"\bdeprecat",
    r"\bpric(e|es|ing)\b", r"\bcosts?\b", r"\bkost(e|et|en)\b", r"\bquota\b", r"\blimits?\b",
    r"\bapi\b", r"\bsdk\b", r"\bendpoint\b", r"\bdocs?\b", r"\bdokumentation\b",
    r"\blatest\b", r"\bcurrent(ly)?\b", r"\baktuell", r"\bneueste[nrs]?\b", r"\bnowadays\b",
    r"\bbest practice", r"\brecommend", r"\bempfehl", r"\bstate of the art\b",
    r"\bvs\.?\b", r"\bversus\b", r"\bcompare[ds]?\b", r"\bvergleich", r"\balternative",
    r"\bwhich\b(?!\s+(file|line|function|test|branch|commit|folder|dir))", r"\bwelche[srn]?\b",
    r"\bshould (i|we)\b", r"\bsoll(te)? (ich|wir)\b", r"\bworth (it|using)\b",
    r"\bhow (do|does|can|should|would) (i|you|we|one)\b", r"\bwie (macht|geht|kann|soll)",
    r"\bwhat (is|are|was|were|does)\b", r"\bwas (ist|sind|war|macht)\b",
    r"\bwhy (is|does|do|are)\b", r"\bwarum\b", r"\bwieso\b",
    r"\bis (it|there) (possible|supported|still)\b", r"\bgibt es\b", r"\bunterst(ü|ue)tzt\b",
    r"\bsupports?\b", r"\bmaintained\b", r"\bstill work", r"\bstimmt das\b",
    r"\berror\b", r"\bexception\b", r"\btraceback\b", r"\bfehlermeldung\b",
    r"\bstandard\b", r"\bspec(ification)?\b", r"\brfc\s?\d", r"\bpaper\b", r"\bstud(y|ie)",
    r"\bmarket\b", r"\bmarkt\b", r"\bcompetitor", r"\bkonkurrenz",
    r"\bresearch\b", r"\brecherche\b", r"\bfind out\b", r"\bherausfinden\b",
]

# Strong enough to fire even inside an otherwise local-looking prompt.
STRONG = [
    r"\bversion(s|en)?\b", r"\bdeprecat", r"\bchangelog\b", r"\bpric(e|es|ing)\b",
    r"\bkost(e|et|en)\b", r"\bapi\b", r"\bdocs?\b", r"\blatest\b", r"\baktuell",
    r"\bbest practice", r"\brecherche\b", r"\bresearch\b",
]

# Purely local/mechanical work — no amount of googling helps.
ANTI_SIGNALS = [
    r"^\s*/", r"\bgit (commit|push|status|diff|add|log)\b", r"\brename\b",
    r"\bthis (file|function|line|repo|test)\b", r"\bdiese[srn]? (datei|funktion|zeile)\b",
]


def main() -> int:
    try:
        if os.path.exists(os.path.join(os.path.expanduser("~"), ".claude", "research-first-off")):
            return 0
        raw = sys.stdin.read()
        prompt = (json.loads(raw).get("prompt") or "") if raw.strip() else ""
    except Exception:
        return 0  # never block a prompt because the gate failed

    if not prompt or len(prompt) < 12:
        return 0

    low = prompt.lower()
    if any(re.search(p, low) for p in ANTI_SIGNALS) and not any(
        re.search(p, low) for p in STRONG
    ):
        return 0
    if any(re.search(p, low) for p in SIGNALS):
        print(REMINDER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
