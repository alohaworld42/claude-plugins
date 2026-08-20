---
name: capabilities
description: Capability checklist — a reminder of what is actually possible in this environment: run real CLIs in the cloud, search the web before answering, check existing tools/connectors before saying "can't", ask for tokens when access is missing, attach repos via add_repo. Use when the user says "what can you do", "capabilities", "capability check", "don't forget what you can do", or when a task needs a capability that is easily overlooked (executing, searching, tool/access checks).
---

# Capability Brief

Recurring problem: available capabilities get forgotten and tasks are "answered" from memory even though the environment can do more. This checklist is the countermeasure. The plugin's `SessionStart` hook (`hooks/hooks.json`) surfaces it automatically at every session start — this skill is the full version you can pull up on demand.

## Checklist

1. **Real environment, not theory.** The shell is real — run CLIs, scripts, git, build tools instead of describing what one could do. Run first, then report.
2. **Look it up instead of guessing.** For anything that may have changed since the knowledge cutoff (versions, prices, APIs, current facts): `WebSearch`/`WebFetch` first, then answer. No memory bluffing.
3. **Check the toolbox before "can't".** `ToolSearch` (deferred tools), `ListConnectors` (connected MCP servers), `SearchMcpRegistry` (available connectors). "I don't have that" only after looking.
4. **Access missing? Ask.** External service needed, access missing (token, key, login) → first check whether it already exists, then ask the user for it specifically. Don't fail silently, don't claim "impossible" wholesale.
5. **Repo out of scope? Attach it.** GitHub repo outside the session scope → `add_repo`, instead of "no access".
6. **Verify before "impossible".** Report infeasibility only after the real attempt produced the error — never from assumption.

## Applying it

Before any refusal ("I can't", "I don't have", "that's not possible") walk points 3–6. Before a factual claim, point 2. For anything executable, point 1.

## Off

Disable the hook: remove the plugin, or delete the `SessionStart` entry from `settings.json`.
