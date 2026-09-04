# cleaning-up-codebases

Systematic codebase cleanup that asks "should this exist?" before "how can I improve this?"

## Purpose

The core failure mode in cleanup work is refactoring code that should be deleted, or adding new abstractions to an already over-abstracted mess. This skill drives the opposite instinct: removal over refactoring, simplification over restructuring, verified before and after every change.

Especially useful on vibe-coded or rapidly developed projects, where code tends to drift from stated intent — features nobody documented, half-finished experiments, alternate implementations left side by side.

## What it does

1. **Reads intent first** — README/CLAUDE.md, design docs, recent git log, dependency manifest — before touching any code, to find the gap between what the project claims to be and what's actually there.
2. **Surveys with automated scans**, not file-by-file reading — dead code, unhandled errors, TODO/FIXME markers, god files, scope creep, language-specific smells.
3. **Establishes a clean baseline** — lint, test, build — before evaluating anything else. A codebase that fails its own checks has a foundation problem, and that's the first finding.
4. **Questions feature existence** before proposing improvements: does this align with the project's purpose, is it actually used, was it ever finished?
5. **Classifies findings into tiers** (T1 safe deletes → T4 architectural changes) instead of one flat list, and works them in that order — T1 before T2 before T3.
6. **Negotiates scope with the owner** rather than assuming what they value; presents findings before prescribing a plan.
7. **Verifies after every change**, not just at the end — build, test, commit, repeat.

## Installation

```
/plugin install cleaning-up-codebases@alohaworld-plugins
```

## Triggers

Reviewing or cleaning a codebase for cruft, dead code, anti-patterns, scope creep, or architectural drift — most often invoked at the start of a cleanup pass or before a larger refactor.
