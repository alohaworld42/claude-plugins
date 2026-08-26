# Instagram-Tipps 26.08.2026 — Claude Code

## Reel 1: unlazy (cooper.simson, DcVSyBvvthb)

Problem: „partial compliance" — Agent meldet fertig, hat 3 Schritte übersprungen.
Fix: Skill **unlazy** — Depth Tree (Task in N Ebenen zerlegen, jedes Blatt volles Zeitbudget), `GATES.md` mit `CHECK:`-Kommandos, optionaler Stop-Hook blockiert „fertig" bei offenen Gates.

Repo: https://github.com/Leonxlnx/unlazy (MIT, v2.1.0 unreleased, kein Tag)

Installiert: `~/.claude/skills/unlazy` (git clone, Selbsttest 12/12 ok)

Nutzung:
```text
/unlazy tree 5 refactor the payment module and verify every migration path
```
`tree N` = Tiefe/„branches". Solo-Task: `templates/gates-leaf.md` → `GATES.md`, dann
`node ~/.claude/skills/unlazy/scripts/gate-check.mjs --status GATES.md`

Stop-Hook (optional, schreibt `.claude/settings.local.json`):
```text
node ~/.claude/skills/unlazy/scripts/install-hooks.mjs
node ~/.claude/skills/unlazy/scripts/install-hooks.mjs --uninstall
```
Ignore: `.unlazy/`, `.unlazy-hook-state.json`, `.claude/settings.local.json`

Prompt aus dem Video (vor dem Skill-Aufruf, für Parallelität):
```text
You are allowed to run multiple sub-agents at the same time. When the plan has independent tasks, dispatch them together in one batch instead of waiting for each one to finish. Only run tasks one after another when a task genuinely needs another task's output. Before dispatching, check the planned file so two agents never edit the same file.
```

## Reel 2: 5 Installs gegen Limit (vektor.fm, DcZZthnRegy)

| # | Tool | Was | Install |
|---|---|---|---|
| 1 | OmniRoute | Lokaler MIT-Gateway, 1 Endpoint, 350 Provider (90+ free), Auto-Failover bei Quota-Ende | https://github.com/diegosouzapw/OmniRoute — `claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream` |
| 2 | claude-mem | Session-übergreifendes Memory (SQLite+Chroma), 65k Stars | https://github.com/thedotmack/claude-mem — `npx claude-mem install` |
| 3 | Headroom | Komprimiert Tool-Output/Logs vor dem LLM, 20 % (Code) bis 60–95 % (JSON) | https://github.com/headroomlabs-ai/headroom — `pip install headroom-ai` (Proxy/MCP/Lib) |
| 4 | claude-code-setup | Anthropic, read-only Repo-Analyse → Hooks/Skills/MCP-Empfehlungen | **schon installiert** (`claude-code-setup:claude-automation-recommender`) |
| 5 | Task Observer | Meta-Skill, loggt Korrekturen → Skill-Verbesserungen | https://github.com/rebelytics/one-skill-to-rule-them-all → `.claude/skills/task-observer/` |

Überschneidungen mit eigenem Setup: #2 ≈ `wrapup`, #3 ≈ `context-mode`, #5 ≈ `tasks/lessons.md`-Regel im workflow-Modul.

Video-Zahlen (Reel-Claims, nicht geprüft): OmniRoute „53k Stars, 1,5 Mrd. Free-Tokens/Monat" — Sekundärquelle nennt 9,3k Stars/1,6 Mrd.; Headroom „77 %" = Needle-in-Haystack-Benchmark, nicht Coding.

Quellen:
- https://github.com/Leonxlnx/unlazy
- https://github.com/diegosouzapw/OmniRoute
- https://github.com/thedotmack/claude-mem
- https://github.com/headroomlabs-ai/headroom
- https://github.com/rebelytics/one-skill-to-rule-them-all
- https://nerdzap.com/news/omniroute-open-source-ai-gateway-free-tokens/
