# capabilities

Surfaces a capability checklist at session start — against forgetting what the environment can actually do.

## Purpose

Recurring pattern: available capabilities get overlooked and tasks are answered from memory instead of using the environment. This plugin reminds Claude of six points at every session start:

1. Run real CLIs in the cloud instead of describing them
2. Search the web before answering (volatile facts)
3. Check existing tools/connectors before saying "can't"
4. Ask for tokens/keys when access is missing
5. Attach out-of-scope repos via `add_repo`
6. Make the real attempt before declaring something "impossible"

## Mechanics

- `hooks/hooks.json` — `SessionStart` hook that surfaces `reminder.txt` as context at every start (hooks are executed by the harness, not the model — that's the only way it fires automatically).
- `skills/capabilities/SKILL.md` — the full version, available on demand ("capability check").

A skill alone only triggers on keywords; the automatic surfacing is the hook's job.

## Installation

```
/plugin install capabilities@alohaworld-plugins
```

Alternatively, without the plugin system (e.g. a remote session): add the `SessionStart` hook directly to `~/.claude/settings.json` and point it at a local copy of `reminder.txt`.
