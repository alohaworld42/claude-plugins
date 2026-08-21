# research-first

The steps a human takes *before* thinking. Ask someone an unfamiliar question
and they google it, skim five results, notice three agree and two don't, decide
which is more plausible — and only then start reasoning. An agent that skips to
the reasoning produces answers that are well-argued, confident, and grounded in
nothing.

The reasoning was never the weak part. The groundwork was missing.

## The six moves

1. **Stop before answering from memory** — memory is a hypothesis, not a source. The tell: an answer with no URL that could have been written a year ago.
2. **Fan out** — 3–5 differently worded queries (jargon / plain language / verbatim error / `X limitations` / primary source). Different phrasings reach different documents; the adversarial one is the only reliable way to find counter-evidence.
3. **Open more than the first hit** — ≥3 sources, diverse in *type*: primary (docs, spec, changelog), practitioner (issue, SO, postmortem), critical ("problems with"). Judge a source by leaving it, not by studying it.
4. **Compare, don't concatenate** — name agreement, name divergence, adjudicate with a reason (recency, primary vs. secondhand, incentive, matches the user's version). Five blogs restating one announcement are one source.
5. **Trace claims to origin** — every load-bearing number goes back to a doc, commit, changelog, or paper. A dead-end trail is itself a finding.
6. **Then think** — unchanged, except the answer now says what it rests on and where the evidence was thin.

## Skip it when

The question is about this repo (grep *is* the search), the fact is stable and
foundational, the user supplied the source, or being wrong is cheap. Research is
a method, not a ritual.

## Why a hook, not just a skill

A skill only fires when the model remembers to reach for it — which is exactly
the failure this plugin exists to fix. So the plugin also ships a
`UserPromptSubmit` gate: a small Python script that reads the prompt, checks it
for research-shaped signals (versions, prices, APIs, comparisons, "how do people
do X", error strings, "what is / why does"), and injects a four-line reminder
**only then**. Purely local work (`git commit`, `rename foo`, "fix this line")
stays silent — a hook that fires on every prompt gets ignored within a day.

Kill switch: `New-Item ~/.claude/research-first-off` (or `touch` it).

## Relation to the neighbours

- **deepfetch** — the escalation path when a source won't open (403/WAF/JS-shell/login). research-first decides *that* you need the page; deepfetch gets it.
- **capabilities** — its session-start checklist includes "look it up instead of guessing". This plugin is that one line expanded into a method with a trigger.
- **restraint** — restraint stops over-delivering; research-first stops under-grounding. Opposite failure modes.

## Triggers

"research", "recherche", "search first", "look it up", "check sources",
"verify that", "don't guess" — plus automatic firing via the prompt gate.

## Origin

- **SIFT** — Mike Caulfield's four moves (Stop, Investigate the source, Find better coverage, Trace claims), via [UChicago Library](https://guides.lib.uchicago.edu/c.php?g=1241077&p=9082322) and [CMU Libraries](https://libguides.cmich.edu/web_research/lateral). Moves 1 and 3–5 are its agent-side translation.
- **Lateral reading** — Sam Wineburg's Stanford History Education Group: professional fact-checkers evaluate a source by leaving the page ([MSU Mankato](https://libguides.mnsu.edu/sourcecredibility/lateralreading)).
- **Query fan-out** — multi-angle query generation as used by generative search ([Kopp Online Marketing](https://www.kopp-online-marketing.com/from-query-refinement-to-query-fan-out-search-in-times-of-generative-ai-and-ai-agents)).
- **Verification-driven orchestration** — VMAO measures answer completeness 3.1 → 4.2 and source quality 2.6 → 4.1 against a single-agent baseline once a verification step checks coverage and re-searches the gaps ([arXiv 2603.11445](https://arxiv.org/html/2603.11445v2)).

## Installation

```
/plugin install research-first@alohaworld-plugins
```

## Ships

- skill `research-first` → `/research-first:research-first`
- `hooks/hooks.json` + `hooks/research_gate.py` (UserPromptSubmit gate, stdlib only)
