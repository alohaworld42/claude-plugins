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

### seo

SEO audit-and-fix workflow. Audits a page or site against a seven-part checklist — crawlability/indexability, on-page, Core Web Vitals, structured data, E-E-A-T content, AI-search (GEO) readiness, plus i18n/local/e-commerce where relevant — then applies fixes directly in the codebase.

- Evidence-backed findings only; no invented scores or traffic predictions.
- Audits raw server HTML first (what crawlers see), rendered DOM second.
- Prioritized findings table, applied fixes with diffs, remaining user actions.

Ships: skill `seo` → `/seo:seo`

Inspired by the excellent [claude-seo](https://github.com/AgriciDaniel/claude-seo) toolkit (MIT) by Daniel Agrici — install that instead if you want the full 25-skill / 18-agent version with SERP data and drift monitoring. This plugin is the single-skill, zero-dependency distillation.

### seo-de

German-language version of the `seo` skill, extended with DACH specifics: Impressum/Datenschutz as legal requirement and E-E-A-T trust signal, umlaut transliteration in URLs (ä→ae, ß→ss), `hreflang` for de-DE/de-AT/de-CH, Swiss ß handling, EUR/CHF product schema. Audits, reports, and communicates in German.

Ships: skill `seo-de` → `/seo-de:seo-de`

## Layout

```
.claude-plugin/marketplace.json
plugins/orchestrator/
  .claude-plugin/plugin.json
  skills/orchestrator/SKILL.md
  agents/sonnet-worker.md
plugins/seo/
  .claude-plugin/plugin.json
  skills/seo/SKILL.md
plugins/seo-de/
  .claude-plugin/plugin.json
  skills/seo-de/SKILL.md
```

## License

MIT
