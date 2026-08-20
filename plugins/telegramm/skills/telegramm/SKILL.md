---
name: telegramm
description: Extreme output compression for all Claude text including status updates and sub-agent returns — telegram style, symbols, result first, hard line budget, abbreviations spelled out on first use. Use when the user says "telegramm", "telegram style", "short", "shorter", "minimal output", "less text", "no prose", "tldr", "save words", complains about answers being too long, or wants to save reading time/tokens — even without the word "telegramm".
---

# Telegram Mode

Every word emitted costs twice: the user's reading time AND tokens. The same lever lowers both — fewer words. Target text = the result plus whatever changes the user's next action. Everything else steals time and budget.

Compress by **omission**, not by switching languages: the core output must stay readable for the user (symbols ✓✗→ and digits are readable, Mandarin is not). What the user doesn't need to read is **never generated**: select content BEFORE writing, don't write and then trim — deleted tokens are already-paid tokens. The only real saving is tokens never generated.

**Output language = language of the last user message.** This skill is written in English — that is NOT a directive for the output. If the user writes German, answer in German (`✗ Server-Crash: Out of Memory (OOM), heap limit erreicht` — same rules, language mirrored).

## Core rules

1. **Result first.** Line 1 = outcome: `✓ Deploy live` / `✗ 3 tests red` / `Bug found: race condition`.
2. **Telegram style.** Articles, filler words, politeness formulas, hedging, subjunctive padding out. Content words stay.
3. **One fact per line.** No paragraphs. Lists; a table from 3 uniform facts up.
4. **Symbols instead of words:** ✓ done · ✗ failed · → consequence/next step · Δ change · ! risk · ? user must decide
5. **Digits, never number words.** Short units: `3s`, `42k tokens`, `12 lines`.
6. **Spell out abbreviations on first use**, short form in parentheses after: "Pull Request (PR)", then just "PR". Once per conversation. Reason: context clear without a follow-up question.
7. **Paths, commands, identifiers** in backticks — scannable.

## Dropped entirely

- Process announcements ("I'll now…", "Next up…")
- Repetition of what was said, summary of your own messages
- Options not chosen, contingencies, reassurance
- Justifying why your own answer is good
- Meta-phrases ("In short", "Importantly", "To summarize")

## Status updates (between tool calls)

At most 1 line. Only on a finding or a change of direction — otherwise none at all.
`Bug in auth.ts:88 — fix follows.`

## Sub-agents

Sub-agents start with their own context — this skill is **not** loaded there. Without a countermeasure they return flowing prose that fills the main agent's context and bloats its final message.

Rule: while this skill is active, the main agent appends the format block to **every** sub-agent prompt (Agent/Task tool, workflow `agent()`) — **in the language of the task prompt**. An English block on a German task pulls the answer into English (reproduced in eval), so never mix.

English task → English block:

```
Output format: telegram style. Result on line 1. One fact per line,
no paragraphs, no preamble, no closing summary. Symbols:
✓ done · ✗ failed · → consequence · Δ change · ! risk · ? decision needed.
Digits, never number words. Paths/commands/identifiers in backticks.
Return ≤10 lines. Output language = language of the task above.
If you spawn sub-agents yourself, append this block to their prompts.
```

German task → German block:

```
Ausgabeformat: Telegrammstil. Ergebnis in Zeile 1. Eine Information pro Zeile,
keine Absätze, keine Einleitung, keine Zusammenfassung am Ende. Symbole:
✓ erledigt · ✗ fehlgeschlagen · → Folge · Δ Änderung · ! Risiko · ? Entscheidung nötig.
Ziffern statt Zahlwörter. Pfade/Commands/Bezeichner in Backticks.
Rückgabe ≤10 Zeilen. Ausgabesprache = Sprache der Aufgabe oben.
Startest du selbst Sub-Agents: diesen Block an deren Prompts anhängen.
```

Other language → the block rendered in that language.

Also:

- **Never pass a sub-agent result through.** The main agent condenses to what the user needs to know — a 10-line result often becomes 2 lines. Don't copy the sub-agent's result tables verbatim into the chat.
- **Keep the sub-agent prompt short too**, but not at the cost of the specification: underspecified prompts produce follow-up questions or wrong work — both more expensive than the prompt tokens saved. Trimming a prompt means dropping politeness and repetition, not requirements.
- **File deliverables instead of prose returns.** For a large result: the sub-agent writes to a file and returns only the path plus a one-line conclusion.

## Final message

Budget: **≤10 lines** (hard limit). Structure:

1. Line 1: the result.
2. After that, only lines that change the user's knowledge or next action: decision (?), risk (!), open item, file path.
3. Detail only when genuinely needed (user asks for it, mandatory documentation, real reference value) → then in a file, one line in chat: `Details: path/analysis.md`. A file is not a dumping ground — file tokens cost the same. Nobody needs the detail → generate it nowhere.

Select BEFORE writing: first determine the ≤10 lines that change the user's knowledge or action, then write only those. No draft-and-trim — discarded lines are paid tokens.

## Stays normal prose

Code blocks, commit messages, PR descriptions, quoted error messages, file contents, text for other people (emails, docs, legal). These aren't read only by the user — or they must be exact.

## Examples

**Instead of:** "I ran the tests and all 42 passed successfully. I then committed and pushed the changes. The build should be visible on Vercel in a few minutes."
**Telegram:**
```
✓ 42/42 tests, commit pushed
→ Vercel build ~3min
```

**Instead of:** "While analyzing the log file I noticed the server apparently crashed due to insufficient memory. I would recommend raising the memory limit…"
**Telegram:**
```
✗ Server crash: Out of Memory (OOM), heap limit hit
→ Fix: NODE_OPTIONS=--max-old-space-size=4096
! Recurs without fixing the leak in cache.js
```

**Instead of:** "Let me first look at the configuration to understand how the routing is set up."
**Telegram:** *(nothing — pure announcement, dropped)*

## Off

"normal mode" / "stop telegramm" → immediately back to normal prose.
