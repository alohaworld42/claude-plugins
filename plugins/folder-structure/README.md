# folder-structure

Gibt jedem Projekt eine saubere, agent-taugliche Ordnerstruktur nach der **Interpretable Context Methodology** (ICM) — Van Clief & McDermott, [arXiv:2603.16021](https://arxiv.org/abs/2603.16021).

## Kernidee

Das Dateisystem IST die Orchestrierung: nummerierte Ordner kodieren die Ausführungsreihenfolge, Markdown-Dateien tragen Prompts und Kontext, `output/`-Ordner sind die Übergabepunkte zwischen Stages. Ein Agent, der die richtigen Dateien im richtigen Moment liest, ersetzt ein Multi-Agent-Framework.

## Was der Skill liefert

- **5-Layer-Kontexthierarchie**: Identität (`CLAUDE.md`) → Routing (`CONTEXT.md`) → Stage-Contract → Referenzmaterial → Arbeitsartefakte
- **Kanonisches Layout** mit `stages/NN_name/`, `_config/`, `shared/`, `setup/`
- **Stage-Contract-Template** (Inputs/Process/Outputs) für jede Stage
- **Migrations-Vorgehen** für bestehende Projekte (Audit → Mapping → Verschieben → Contracts schreiben)
- **Grenze für Code-Repos**: ICM strukturiert Agent-Workflows, nicht Source-Trees — `src/`, `tests/` etc. bleiben bei den Konventionen des Ökosystems

## Trigger

„folder structure", „ordnerstruktur", „organize this project", „scaffold", „workspace setup", „ICM", „restructure the repo" — oder Start eines neuen mehrstufigen Projekts.

## Installation

```
/plugin install folder-structure@alohaworld-plugins
```
