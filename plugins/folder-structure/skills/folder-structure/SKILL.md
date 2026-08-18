---
name: folder-structure
description: Give any project a clean, agent-ready folder structure based on the Interpretable Context Methodology (ICM, arXiv:2603.16021) — numbered stage folders, five-layer context hierarchy, stage contracts in CONTEXT.md files, output handoffs between stages. Use when the user says "folder structure", "ordnerstruktur", "organize this project", "scaffold", "workspace setup", "project layout", "ICM", "restructure the repo", or starts a new multi-step project/workflow that needs a directory layout.
---

# Folder Structure (ICM)

Source: "Interpretable Context Methodology: Folder Structure as Agent Architecture" (Van Clief & McDermott, arXiv:2603.16021). Core idea: the filesystem IS the orchestration. Numbered folders encode execution order, markdown files carry prompts and context, output folders are the handoff points. One agent reading the right files at the right moment replaces a multi-agent framework.

## The five-layer context hierarchy

| Layer | File/location | Question it answers | Size |
|---|---|---|---|
| 0 | `CLAUDE.md` (workspace root) | "Where am I?" — workspace identity, what the folder structure contains | ~800 tok |
| 1 | `CONTEXT.md` (workspace root) | "Where do I go?" — task routing: which stage handles what | ~300 tok |
| 2 | `stages/NN_name/CONTEXT.md` | "What do I do?" — the stage contract (Inputs/Process/Outputs) | 200–500 tok |
| 3 | `references/`, `_config/`, `shared/` | "What rules apply?" — stable reference material, same every run | 500–2k tok |
| 4 | `stages/NN_name/output/` | "What am I working with?" — working artifacts, change every run | varies |

Layer 3 = the factory (internalize as constraints: write *like this*, use *these* conventions). Layer 4 = the product (process as input: transform *this* material). Never mix them in one undifferentiated pile — the folder structure pre-sorts context so the model doesn't have to.

## Canonical workspace layout

```
workspace/
├── CLAUDE.md              # Layer 0: identity — what this workspace is, map of the structure
├── CONTEXT.md             # Layer 1: routing — task → stage, shared resources
├── stages/
│   ├── 01_research/
│   │   ├── CONTEXT.md     # Layer 2: stage contract
│   │   ├── references/    # Layer 3: stage-specific reference material
│   │   └── output/        # Layer 4: this stage's deliverables (next stage's input)
│   ├── 02_script/
│   │   ├── CONTEXT.md
│   │   ├── references/
│   │   └── output/
│   └── 03_production/
│       ├── CONTEXT.md
│       ├── references/
│       └── output/
├── _config/               # Layer 3: workspace-wide config (voice.md, design-system.md, conventions.md)
├── shared/                # Layer 3: reference material used by several stages
└── setup/
    └── questionnaire.md   # setup questions asked once when configuring the workspace
```

Naming rules:
- Stage folders: `NN_lowercase-name` — two-digit zero-padded number encodes execution order.
- Underscore prefix (`_config/`) = infrastructure, not a stage.
- Everything plain text: markdown and JSON only. No binary formats, no databases — any tool and any human can read/edit every artifact.

## Stage contract template (every stage's CONTEXT.md)

```markdown
## Inputs
- Layer 4 (working): ../01_research/output/
- Layer 3 (reference): ../../_config/voice.md
- Layer 3 (reference): references/structure.md

## Process
Write a script based on the research output.
Follow the structure in structure.md.
Match the tone described in voice.md.

## Outputs
- script_draft.md -> output/
```

The Inputs list is the control point: it declares exactly which files (and which layers) the stage loads — explicit, editable, auditable. An agent executing a stage loads ONLY what the contract names; total context per stage should land at 2k–8k tokens, never the monolithic everything-pile.

## Five design principles (apply when structuring)

1. **One stage, one job.** A stage that fetches doesn't filter; a stage that filters doesn't format. Split until each folder has a single transformation.
2. **Plain text as the interface.** Stages communicate through markdown/JSON files in `output/`.
3. **Layered context loading.** Load only the current stage's declared inputs. Prevention beats compression.
4. **Every output is an edit surface.** Humans review/edit `output/` files between stages; the next stage reads whatever is there. Never make a handoff that a human can't open in a text editor.
5. **Configure the factory, not the product.** User preferences, brand, style → `_config/` once. Each run produces a new deliverable from the same configuration. Recurring fix? Edit the source (contract/reference), not the output — editing output fixes this run, editing source fixes every future run.

## Applying to a project

**New project:** ask (or infer) the workflow stages, scaffold the canonical layout, write CLAUDE.md (identity + structure map), CONTEXT.md (routing), one stage contract per stage. Seed `_config/` from the user's stated preferences; put open setup questions in `setup/questionnaire.md`.

**Existing project:** audit first, then migrate:
1. Map current files → layers (identity? routing? per-step instructions? stable reference? per-run artifacts?).
2. Identify the workflow's sequential stages; create `stages/NN_name/` for each.
3. Move stable rules/conventions into `_config/` or `references/`; move per-run artifacts into the owning stage's `output/`.
4. Write the missing CONTEXT.md contracts with explicit Inputs lists.
5. Delete nothing without confirmation — propose moves as a plan when the restructure is large or destructive.

**Code repositories:** ICM targets content/agent workflows, not source trees. For a software repo, apply ICM to the agent-facing scaffolding (docs, prompts, pipeline folders) and leave the language ecosystem's conventions (`src/`, `tests/`, etc.) intact — never force numbered stage folders onto source code.

## Traversal rule for agents

Read Layer 0 → Layer 1 → the current stage's Layer 2, then load only the contract's declared Layer 3/4 inputs. Sub-agents get the same treatment: the delegating agent fills sub-agent prompts from the same CONTEXT.md hierarchy — the folder structure is both the human's control surface and the orchestration logic.
