---
name: github
description: GitHub-Operationen über die gh CLI — Repo anlegen und veröffentlichen, Sichtbarkeit ändern, Pull-Request-Workflow, Releases, Issues. Nutzen wenn der User sagt "repo anlegen", "repo erstellen", "veröffentlichen", "auf github pushen", "release", "PR erstellen", "issue anlegen", "repo privat/public stellen", oder GitHub-Verwaltung jenseits von git push braucht.
---

# GitHub-Operationen

Alles läuft über die **gh CLI** — sie nutzt den Token des eingeloggten Users und kann damit, was scoped App-Integrationen oft nicht dürfen: Repos anlegen, Sichtbarkeit ändern, Releases veröffentlichen.

## Immer zuerst: Verfügbarkeit prüfen

```bash
gh auth status
```

- **OK** → weiter mit den Rezepten unten.
- **`gh` fehlt oder kein Login** → sag dem User genau das, mit dem Fix: `gh auth login` bzw. Installation (https://cli.github.com). Nicht raten, nicht mit halben Rechten weiterprobieren.
- **Remote-Umgebung mit GitHub-App statt gh** (Claude Code Web/Remote): App-Scope kann i. d. R. **keine Repos anlegen und keine Sichtbarkeit ändern** (403 „Resource not accessible by integration"). Dann: alles vorbereiten (Dateien, Struktur, Commits), dem User die 1–2 manuellen Schritte auf github.com nennen, nach Rückmeldung pushen.

## Repo anlegen & veröffentlichen

Neues Repo aus vorhandenem Verzeichnis:

```bash
gh repo create <name> --private --source . --push
```

- `--private` ist der Default dieses Skills. **`--public` nur, wenn der User Veröffentlichung ausdrücklich verlangt hat** — und dann vor dem Befehl in 1 Zeile bestätigen lassen, was public wird.
- Vor jedem ersten Push in ein public Repo: kurz auf Secrets prüfen (`.env`, Keys, Tokens in der History). Fund → stoppen und melden, nicht pushen.
- Leeres Repo ohne lokalen Code: `gh repo create <name> --private --clone`.

Sichtbarkeit ändern:

```bash
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

Public→privat bricht bestehende Clones/Installationen Dritter — vorher 1 Zeile Risiko nennen, Bestätigung abwarten.

## Pull-Request-Workflow

```bash
git checkout -b <branch> && git push -u origin <branch>
gh pr create --draft --title "..." --body "..."
gh pr merge <nr> --squash --delete-branch
```

- PRs als Draft anlegen, außer der User will direkt mergen.
- PR-Beschreibung: was und warum, normale Prosa — sie ist Doku für Dritte.
- Repo-PR-Template (`.github/pull_request_template.md`) respektieren, wenn vorhanden.

## Releases

```bash
gh release create v<version> --title "v<version>" --notes "..."
```

Version aus dem Projekt lesen (`package.json`, `plugin.json`, Tags) — nicht erfinden. Notes: Änderungen seit letztem Release, aus `git log <lasttag>..HEAD`.

## Issues

```bash
gh issue create --title "..." --body "..."
gh issue list --state open
```

Vor dem Anlegen mit `gh issue list --search "..."` auf Duplikate prüfen.

## Sicherheitsregeln (nicht verhandelbar)

- **Nie ohne explizite User-Anweisung:** Repo löschen/archivieren, auf public stellen, Force-Push auf geteilte Branches, Releases löschen.
- `gh repo delete` nur nach wörtlicher Bestätigung mit Repo-Namen durch den User.
- Tokens/Secrets nie in Befehle, Logs oder Commits schreiben.
- Bei 403/404 auf existierende Repos: erst Rechte-Problem melden (App-Scope? Login?), nicht blind wiederholen.
