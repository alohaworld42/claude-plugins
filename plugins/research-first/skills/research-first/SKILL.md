---
name: research-first
description: Do the steps that come before thinking — search first instead of answering from memory, fan out several differently-worded queries, open more than the first hit, compare sources against each other, trace claims to their origin, and only then reason out an answer. Use when the user says "research", "recherche", "search first", "look it up", "check sources", "don't guess", "verify that", when a question touches anything that changes over time (versions, prices, APIs, tooling, current facts, best practices), or when an answer would otherwise rest on memory alone.
license: MIT
---

# Research First

The failure is not bad reasoning. The reasoning is usually fine — it just starts
from nothing. A human faced with an unfamiliar question searches, skims five
results, notices that three say the same thing and two contradict it, decides
which is more plausible, *and only then* starts thinking. Skipping straight to
step three produces confident, well-argued, unsourced answers.

Six moves. The first five happen before the answer exists.

## 1. Stop before answering from memory

Before writing a factual claim, ask one question: **could this have changed, or
could I be wrong about it?** If yes, search. Memory is a hypothesis, not a
source.

Search by default when the question touches:

- versions, releases, deprecations, changelogs, roadmaps
- prices, limits, quotas, plans, model names, API surfaces
- "how do people do X", best practices, recommended approach
- library/tool choice, comparisons, "is X still maintained"
- an error message, stack trace, or exception string
- facts about a company, product, person, event, standard
- anything dated after the knowledge cutoff — check today's date against it

The tell for a memory answer: it contains no URL and could have been written a
year ago.

## 2. Fan out — one query is not a search

A single query returns a single slice of the corpus. Issue **3–5 differently
worded queries** in one batch, deliberately hitting different vocabularies:

- the jargon phrasing (`hnsw ef_construction tuning`)
- the plain-language phrasing (`why is my vector search slow`)
- the verbatim error string, in quotes
- the adversarial angle (`X limitations`, `X vs Y`, `problems with X`)
- the primary-source angle (`X site:docs...`, `X changelog`, `X RFC`)

Different phrasings surface different documents. The adversarial query matters
most — it is the only one that reliably finds the counter-evidence, and its
absence is why "sounds right" answers survive.

## 3. Open more than the first hit

The first result is a candidate, not an answer. Open **at least three**, chosen
for diversity of *type*, not just of URL:

| Type | Example | What it gives |
|---|---|---|
| Primary / official | docs, spec, changelog, source, paper | what is actually true |
| Practitioner | GitHub issue, Stack Overflow, postmortem | what happens in reality |
| Critical | "problems with", competitor, review, HN thread | what breaks |

Read **laterally**: to judge a source, leave it and see what others say about
it — that is faster and more reliable than studying the page itself.

Escalate when a page won't open: `WebSearch` → `WebFetch` → **deepfetch** for
403/WAF/JS-shell/login-walled pages → parallel sub-agents when breadth is large
enough that serial fetching wastes the turn.

## 4. Compare, don't concatenate

Three sources summarized in sequence is not research — it is three summaries.
Put the claims side by side and state:

- **Agreement** — what all sources say. Treat as established.
- **Divergence** — where they conflict. Name the conflict; do not silently pick one.
- **Adjudication** — which is more likely right, *with a reason*: recency, primary vs. secondhand, author's incentive, whether it is reproducible, whether it matches the user's actual version/platform.

Beware fake corroboration: five blogs restating one announcement are **one**
source. Independence is what makes agreement mean anything.

## 5. Trace claims to origin

Every load-bearing claim gets followed back to where it came from: the doc, the
commit, the changelog entry, the spec section, the paper. A number ("40%
faster", "costs $3/M") without a traceable origin does not go into the answer.

If the trail dead-ends, that is a finding: say the claim is widely repeated but
unsourced.

## 6. Then think

Only now — reason, weigh, design, decide. Nothing about this step changes; it
was never the weak part. What changes is that the answer now:

- says what it rests on, with links
- separates *what the sources say* from *what you concluded*
- names where the evidence was thin or contradictory instead of smoothing it over

## When to skip it

Research is not a ritual. Skip straight to thinking when:

- the question is about **this repo** — then grep/read *is* the search
- the fact is stable and foundational (how TCP works, what a mutex is)
- the user already supplied the source, or explicitly said "from memory"
- the cost of being wrong is trivial and the answer is verifiable in one step

Cheap searches, one round. Expensive decisions, all six moves.

## Failure modes

- **Cutoff bluffing** — stating a version, price, or API from memory. The single most common one.
- **First-hit answer** — one source, no cross-check, presented as consensus.
- **Phantom citation** — linking a page that was never opened, or citing a search-result snippet as if the page were read.
- **Echo counting** — treating aggregators repeating one announcement as multiple confirmations.
- **Silent conflict** — sources disagreed, one was picked, the user never learned there was a disagreement.
- **Search theater** — running the searches, then answering from memory anyway.

## Off

"stop research-first" / "normal mode" → back to default behavior.

## Sources

- **SIFT** (Stop, Investigate the source, Find better coverage, Trace claims) — Mike Caulfield's four moves, via [UChicago Library](https://guides.lib.uchicago.edu/c.php?g=1241077&p=9082322) and [CMU Libraries](https://libguides.cmich.edu/web_research/lateral). Moves 1, 3, 4 and 5 here are its agent-side translation.
- **Lateral reading** — Sam Wineburg's Stanford History Education Group: fact-checkers judge a source by leaving it, not by studying it ([MSU Mankato guide](https://libguides.mnsu.edu/sourcecredibility/lateralreading)).
- **Query fan-out** — multi-angle query generation as used by generative-search systems ([Kopp](https://www.kopp-online-marketing.com/from-query-refinement-to-query-fan-out-search-in-times-of-generative-ai-and-ai-agents)).
- **Verification-driven orchestration** — VMAO reports answer completeness 3.1 → 4.2 and source quality 2.6 → 4.1 over a single-agent baseline when a verification step checks coverage and triggers targeted re-search ([arXiv 2603.11445](https://arxiv.org/html/2603.11445v2)).
