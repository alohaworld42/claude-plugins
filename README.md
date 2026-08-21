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

### telegramm

Extreme output brevity for every Claude text — status updates included. Telegraph style, symbols (✓✗→Δ!?), result-first, hard line budget. Saves the user's reading time and tokens by selecting content *before* writing, not drafting then cutting: discarded tokens are already paid tokens.

Ships: skill `telegramm` → `/telegramm:telegramm`

Full write-up incl. eval methodology and benchmark results: [plugins/telegramm/README.md](plugins/telegramm/README.md).

### wrapup

Cross-session memory. At the end of a session, write a compact digest (decisions + why, gotchas, current state, open threads, pointers) to a local store; at the start of the next one, pull back only what's relevant instead of rebuilding context.

The saving comes from selective loading, not compression: `INDEX.md` is one line per session, `recall.py` ranks matching digests, and only the relevant digest gets read.

- Local-first: plain markdown under `~/.claude/wrapup/`, no external service, nothing to break.
- Optional **Notion mirror** (recommended second store): pushes the digest into a "Claude Session Log" database via Notion's official API and MCP server, giving you workspace-wide search, phone access, and structured SQL filters over every past session.
- Optional `--push-notebooklm` mirrors into NotebookLM (Gemini Notebook) instead, for its media features — via the unofficial `notebooklm-py` CLI. Google has no public NotebookLM API (as of 2026-08), so prefer Notion; if the CLI is absent the push reports `skipped` and the local digest is written anyway.

Either way the external store is the mirror, never the foundation — a service change must not be able to erase your memory.

Ships: skill `wrapup` → `/wrapup:wrapup`, plus `scripts/wrapup.py` and `scripts/recall.py`

### deepfetch

Five-tier fetch escalation for pages a plain fetch can't reach: `direct → public-route → tls → browser → cookies (opt-in) → browser+cookies`. Built to cover everything [insane-search](https://github.com/fivetaku/insane-search) and [playwright-bot-bypass](https://github.com/greekr4/playwright-bot-bypass) do, plus the one gap neither closes: a consent-gated **cookies tier** that reuses the user's own already-authenticated browser session for login-walled pages — the same access they already have by hand, never a credential bypass.

- Stops honestly at real login/paywall/captcha/rate-limit walls — reports why instead of faking success.
- Degrades cleanly with zero optional dependencies installed; `setup.py` reports exactly what's missing and the install command.
- Cookies tier is off by default, requires explicit per-domain consent (`--allow-domain`) the agent must obtain from the user in chat first, and never persists a cookie value anywhere.

Ships: skill `deepfetch` → `/deepfetch:deepfetch`, plus `scripts/deepfetch.py` (CLI) and 8 supporting modules.

Verified live before shipping — 6 module self-tests, real network calls, 2 real bugs found and fixed with evidence: [plugins/deepfetch/README.md](plugins/deepfetch/README.md).

### research-first

The steps that come *before* thinking. A human meeting an unfamiliar question searches, skims several results, notices where they agree and where they don't, and only then reasons. An agent that skips to the reasoning writes confident, well-argued, ungrounded answers.

Six moves: stop before answering from memory → fan out 3–5 differently worded queries (jargon / plain / verbatim error / `X limitations` / primary source) → open ≥3 sources of *different type* → compare and adjudicate instead of summarizing in sequence → trace load-bearing claims to their origin → then think.

- Ships a `UserPromptSubmit` gate (stdlib Python) that detects research-shaped prompts and injects a four-line reminder — because a skill that must be remembered is exactly the failure mode. Local work (`git commit`, `rename foo`) stays silent; kill switch `~/.claude/research-first-off`.
- Built on Caulfield's SIFT and Wineburg's lateral reading, plus query fan-out and verification-driven orchestration from the agent literature.
- Pairs with `deepfetch`: research-first decides a page is needed, deepfetch gets it past the 403.

Ships: skill `research-first` → `/research-first:research-first`, plus `hooks/research_gate.py`.

## Contributing a plugin

Each plugin directory should carry its own `README.md` (sibling to `.claude-plugin/` and `skills/`) explaining what it does and why. Where the skill was validated with the skill-creator eval loop (fixtures, with/without-skill subagent comparison, benchmark), include the methodology and results there instead of asserting effectiveness without evidence — see `plugins/telegramm/README.md` for the pattern.

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
plugins/telegramm/
  .claude-plugin/plugin.json
  skills/telegramm/SKILL.md
plugins/wrapup/
  .claude-plugin/plugin.json
  skills/wrapup/SKILL.md
  skills/wrapup/scripts/{wrapup,recall}.py
plugins/deepfetch/
  .claude-plugin/plugin.json
  skills/deepfetch/SKILL.md
  skills/deepfetch/scripts/{deepfetch,common,classify,extract,tier_direct,tier_tls,tier_browser,tier_cookies,setup}.py
plugins/research-first/
  .claude-plugin/plugin.json
  skills/research-first/SKILL.md
  hooks/{hooks.json,research_gate.py}
```

## License

MIT
