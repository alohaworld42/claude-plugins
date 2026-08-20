# folder-structure

Gives any project a clean, agent-ready folder structure based on the **Interpretable Context Methodology** (ICM) — Van Clief & McDermott, [arXiv:2603.16021](https://arxiv.org/abs/2603.16021).

## Core idea

The filesystem IS the orchestration: numbered folders encode execution order, markdown files carry prompts and context, `output/` folders are the handoff points between stages. One agent reading the right files at the right moment replaces a multi-agent framework.

## What the skill delivers

- **Five-layer context hierarchy**: identity (`CLAUDE.md`) → routing (`CONTEXT.md`) → stage contract → reference material → working artifacts
- **Canonical layout** with `stages/NN_name/`, `_config/`, `shared/`, `setup/`
- **Stage contract template** (Inputs/Process/Outputs) for every stage
- **Migration procedure** for existing projects (audit → mapping → move → write contracts)
- **Boundary for code repos**: ICM structures agent workflows, not source trees — `src/`, `tests/` etc. keep their ecosystem's conventions

## Triggers

"folder structure", "organize this project", "scaffold", "workspace setup", "ICM", "restructure the repo" — or the start of a new multi-step project.

## Installation

```
/plugin install folder-structure@alohaworld-plugins
```
