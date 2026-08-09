# github

GitHub-Verwaltung über die gh CLI — für alles, was `git push` allein nicht kann.

## Zweck

Scoped App-Integrationen (z. B. Claude Code Remote) dürfen oft keine Repos anlegen und keine Sichtbarkeit ändern. Die gh CLI mit User-Login kann es. Dieser Skill gibt Claude die Rezepte und — wichtiger — die Leitplanken:

- **Repo anlegen & veröffentlichen** (`gh repo create`), Default privat, public nur auf ausdrücklichen Wunsch mit Bestätigung
- **Sichtbarkeit ändern** mit Risiko-Hinweis (public→privat bricht fremde Clones/Installationen)
- **PR-Workflow** (Draft-PRs, Squash-Merge, Branch-Cleanup)
- **Releases & Issues** (Versionen aus dem Projekt lesen, Duplikat-Check)
- **Secret-Check** vor erstem Push in public Repos

Ohne gh CLI (Remote-Umgebung mit App-Scope) bereitet der Skill alles vor und nennt dem User die 1–2 manuellen Schritte, statt an 403-Fehlern zu scheitern.

## Installation

```
/plugin install github@alohaworld-plugins
```

Voraussetzung: [gh CLI](https://cli.github.com) installiert und eingeloggt (`gh auth login`).
