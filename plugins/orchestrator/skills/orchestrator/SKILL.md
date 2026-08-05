---
name: orchestrator
description: AI model routing protocols — Opus orchestrates, Sonnet sub-agents execute, max 3 in parallel. Use when the user says "orchestrator", "orchestrator mode", "orchestrate this", "delegate this", "route models", "model routing", "fan out workers", or asks to split work between Opus and Sonnet.
---

# AI Model Routing Protocols

Run the current task as orchestrator + workers. The main session is the orchestrator; it spends its expensive tokens on judgment and delegates everything else.

## Orchestrator Mode (Opus — main session)

Keep only high-judgment work in the main session:

- System design and architecture decisions
- Risk identification before changes land
- Breaking refactorings into milestones
- Writing the contracts/specs for workers — they are small, you write them
- Reviewing and integrating worker output — verify, never trust blind

Do not write boilerplate here. If you catch yourself doing mechanical edits in the main session, that work belonged to a worker.

## Execution Mode (Sonnet — `sonnet-worker` sub-agent)

Delegate via the Agent tool with `subagent_type: "sonnet-worker"` (ships with this plugin):

- Isolated modules, fully specified
- Component generation
- Unit tests
- Routine debugging, mechanical edits, lookups

Each worker gets a self-contained contract:

```
Goal:        one sentence, the observable outcome
Files:       exact paths this worker owns — no others
Context:     the interfaces/types it must match, inline
Acceptance:  the command that proves it works (test, build, lint)
```

Cut the work so contracts are **disjoint** — two workers must never own the same file, or they overwrite each other.

Escalate to an Opus worker (`model: "opus"`, `effort: "high"`) when taste shapes the result: UI and frontend work, design implementation, tricky integrations. Sonnet is for specified work, not for judgment.

## Sub-Agent Cap

**Max 3 active Sonnet sub-agents at any time.** This preserves token capacity.

- Spawn up to 3 in parallel — one message, multiple Agent calls.
- Queue the rest. Spawn the next only when one finishes.
- Never fan out the whole backlog at once.

If a milestone needs more than 3 contracts, that is a queue, not a reason to raise the cap.

## Loop

1. Plan milestones and name the risks (orchestrator).
2. Cut the next milestone into ≤3 disjoint contracts.
3. Spawn ≤3 workers in parallel.
4. Review each result, run the acceptance command yourself, integrate.
5. Repeat until the milestone is done, then take the next milestone.

Report to the user per milestone, not per worker.
