# telegramm

What the skill is for, how it was tested, how efficient it is.

## Purpose

Every word emitted costs twice: the user's reading time AND tokens — same lever, fewer words lowers both. `telegramm` enforces result-first, telegram style, symbols instead of prose, and a hard line budget for status updates and final messages.

Compression happens through **selection before writing**, not through foreign-language compression (no Mandarin trick) and not through write-then-trim — discarded lines are already-paid tokens. Details: [SKILL.md](skills/telegramm/SKILL.md).

## Sub-agents (since 1.1.0)

Sub-agents start with their own context, where the skill isn't loaded — so their returns kept coming back as flowing prose and bloated the main agent's final message. Since 1.1.0 the skill contains a format block that the main agent appends to every sub-agent prompt, plus the rule to condense sub-agent results instead of passing them through.

## Eval methodology

3 test cases, one subagent **with** the skill against a baseline subagent **without**, identical prompt, same model (Sonnet, low effort):

| Eval | Task | Language |
|---|---|---|
| `eval-0-debug-report` | Find + fix a bug in `calc.js` and report | German |
| `eval-1-multistep-status` | Create a mini Node project, report progress | German |
| `eval-2-log-analysis` | Read a crash log, report cause + fix | English |

Fixtures under `fixtures/` (repo with the eval workspace, not part of the plugin). Assertions checked per case (content correct? format followed?), aggregated in `benchmark.json`.

## Results (iteration 1, 2026-08-05)

| Eval | Words with skill | Words without | Δ | Pass with | Pass without |
|---|---|---|---|---|---|
| eval-0 | 39 | 48 | −19% | 4/4 | 4/4 |
| eval-1 | 29 | 53 | −45% | 5/5 | 4/5 |
| eval-2 | 58 | 251 | **−77%** | 5/6 | 5/6 |

Savings grow with task size / baseline length. No information loss on the content assertions (cause, fix, next step — present everywhere).

**Bug found:** eval-2 with the skill answered in German although the user prompt was English — the skill's German wording had overridden the language choice. Fix: explicit rule "output language = language of the last user message" plus an English example in the skill. Re-verified afterwards.

**Iteration 2** (rule "never generate tokens instead of trimming" sharpened): retest of eval-1 shows further compression — status updates 2→0, final message 29→~20 words, same information content.

## Results (iteration 3, 2026-08-08) — retest: token savings, symbols, English

New run with 3 configurations (baseline without skill · skill with symbols · skill variant without symbols, status as words) on 2 tasks, each a Sonnet subagent, identical task prompt. What was tested is the sub-agent format block from 1.1.0 — the part of the skill that in practice gets appended to sub-agent prompts.

**Token savings** (words / characters of the return; tokens ≈ characters ÷ 3):

| Task | Baseline | Skill with symbols | Skill without symbols |
|---|---|---|---|
| T1 bug-fix report (German) | 73 w / 633 ch | 31 w / 377 ch (**−58% / −40%**) | 52 w / 514 ch (−29% / −19%) |
| T2 crash-log analysis (English) | 379 w / 2,619 ch | 85 w / 740 ch (**−78% / −72%**) | 111 w / 809 ch (−71% / −69%) |

No loss in substance: every run found the off-by-one bug (and fixed it correctly in the file) or the OOM cause (unbounded cache growth) including fix and residual risk.

**Are symbols necessary?** Yes — keep them. The variant without symbols was consistently longer (T1: +36% characters, T2: +9%) and produced more filler lines ("Status: … done; … open"). Symbols don't just save the words they replace (`✓` vs. "done and fixed"), they also discipline the structure: one marker per line instead of prose openings. The effect is largest on short answers.

**Does the skill work in English?** After a fix: yes. The retest reproduced the language bug from iteration 1 in a new place — the **German** format block from 1.1.0 pulled English tasks into German (both skill variants answered in German to an English prompt; the line "output language = language of this prompt" wasn't enough, because the block itself is part of the prompt). Fix in 1.2.0: the block is appended in the **language of the task prompt**, with the English version ready in the skill. Re-test verified: answer fully in English, 10 lines, format followed, −69% words against baseline.

## Propagation test (iteration 3b, 2026-08-08)

Additionally tested: whether a main agent with the skill loaded actually **follows** the sub-agent rule (not just whether the block works): 2 main agents (Sonnet) got SKILL.md as an active skill and had to delegate a log analysis to their own sub-agent; the exact forwarded prompt was checked.

| Test | Block appended? | Block language correct? | Return condensed instead of passed through? |
|---|---|---|---|
| Main agent German | ✓ verbatim | ✓ German | ✓ 10 → 5 lines |
| Main agent English | ✓ verbatim | ✓ English (new 1.2.0 rule) | ✓ |

Gap found: the block only bound the first level — a sub-agent that spawns its own sub-agents didn't pass it on. Fix: the block now contains a forwarding line ("If you spawn sub-agents yourself, append this block to their prompts"), making propagation transitive.

What remains untestable from the inside is the **triggering** of the skill in the main chat (description matching by the harness on "short", "tldr" etc.) — that's decided by the platform, not by the skill's content.

## Limits

- `runs_per_configuration: 1` — quick validation, not a large benchmark with variance (stddev). Applies to iteration 3 as well.
- Baseline = Sonnet subagent with `effort: low`, terser out of the box than a standard assistant without the skill — real-world savings are probably higher than measured here.
- Raw data (fixtures, `benchmark.json`, per-run reports) lives in `~/.claude/skills/telegramm-workspace/iteration-1/` — not part of this repo.
