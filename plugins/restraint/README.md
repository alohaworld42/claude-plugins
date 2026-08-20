# restraint

Four boundaries against an agent's eagerness. Bad outputs are rarely a knowledge
gap — they're overreach: files rewritten that nobody mentioned; guessing instead
of asking; a system built for a one-liner. Eagerness can't be fixed with *more*
instructions, only by removing.

## The four boundaries

1. **Write less** — the smallest output that fully does the job. No unasked error handling, config, or generality.
2. **Only what was asked** — the prompt is the scope, not a starting point to expand. Match existing style; clean up only your own orphaned imports, name foreign dead code instead of deleting it.
3. **Verify before "done"** — "done" is a claim that must be true. Turn vague tasks into verifiable ones first ("fix bug" → a test that reproduces it, then green).
4. **Ask instead of guessing** — one sharp question on genuine ambiguity. Present interpretations instead of picking silently, push back when a simpler way exists, name your confusion.

**Tradeoff:** caution over speed. Use judgment on trivial tasks — restraint is not paralysis.

## Distinction from `stfu`

`stfu` = no commentary, no unsolicited opinion (tone). `restraint` = no
unsolicited scope, no over-delivering (extent). They complement each other.

## Triggers

"restraint", "stop being eager", "don't over-engineer", "follow the prompt",
"don't touch what I didn't ask for", "stop guessing".

## Origin

- The "one file, four boundaries" concept from an Instagram reel by [@jackroberts___](https://www.instagram.com/p/DcOwUcySo8w/) on prompt discipline with Claude.
- Push-back, surgical-change and goal-driven rules (v1.1.0) adapted from [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (MIT, forrestchang) — derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

## Installation

```
/plugin install restraint@alohaworld-plugins
```
