# claude-plugins

A Claude Code plugin marketplace.

## Install

```bash
claude plugin marketplace add alohaworld42/claude-plugins
```

```bash
claude plugin install orchestrator@alohaworld-plugins
```

Or from inside Claude Code: `/plugin marketplace add alohaworld42/claude-plugins`, then `/plugin install orchestrator@alohaworld-plugins`.

## Plugins

### orchestrator

AI model routing protocols. Turns the main session into an orchestrator that delegates instead of grinding.

- **Orchestrator mode (Opus)** — system design, risk identification, milestone breakdown, contract writing, review and integration.
- **Execution mode (Sonnet)** — isolated modules, component generation, unit tests, routine debugging, handed to the bundled `sonnet-worker` sub-agent.
- **Sub-agent cap** — max 3 active Sonnet workers at a time, to preserve token capacity. The rest queue.

Ships:

- skill `orchestrator` → `/orchestrator:orchestrator`
- sub-agent `sonnet-worker` (Sonnet, low effort)

## Layout

```
.claude-plugin/marketplace.json
plugins/orchestrator/
  .claude-plugin/plugin.json
  skills/orchestrator/SKILL.md
  agents/sonnet-worker.md
```

## License

MIT
