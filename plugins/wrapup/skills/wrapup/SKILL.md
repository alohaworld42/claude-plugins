---
name: wrapup
description: Session-Gedächtnis über Sessions hinweg — am Ende einer Session einen kompakten Digest speichern (Entscheidungen, Gotchas, Stand, offene Punkte) und am Anfang der nächsten gezielt zurückholen, statt Kontext neu aufzubauen. Nutzen wenn der User sagt "wrapup", "wrap up", "session speichern", "merk dir das für nächstes Mal", "was hatten wir letztes Mal", "worauf sind wir stehengeblieben", "erinnerst du dich an", eine Session abschließt, oder nach früheren Entscheidungen/Fixes fragt.
---

# Wrapup — Gedächtnis über Sessions

Jede neue Session startet bei null. Kontext neu aufbauen kostet Tokens und Zeit — und was in der letzten Session entschieden wurde, geht verloren. Dieser Skill löst das mit zwei Bewegungen: **am Ende speichern** (`wrapup.py`), **am Anfang gezielt holen** (`recall.py`).

Die Ersparnis kommt nicht vom Komprimieren, sondern vom **selektiven Laden**: `INDEX.md` ist winzig (1 Zeile pro Session), `recall.py` zeigt nur passende Treffer, und erst dann wird ein einzelner Digest gelesen. Nie die ganze Historie.

Store: `~/.claude/wrapup/` (`sessions/*.md` + `INDEX.md`). Override per `WRAPUP_STORE`.
Skripte: `${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/`.

## Speichern (Session-Ende)

Nur das schreiben, was eine **künftige Session** wissen muss. Es geht nicht um ein Protokoll — es geht darum, dass das nächste Ich nicht dieselbe Sackgasse noch mal läuft.

Rein gehört:
- **Entscheidungen + Begründung.** „X statt Y, weil Z." Ohne das Warum wird die Entscheidung beim nächsten Mal neu diskutiert.
- **Gotchas.** Was überraschend war, kaputt ging, oder nur mit einem Trick lief. Der wertvollste Teil — das steht in keiner Doku.
- **Stand.** Wo die Sache jetzt steht, in einem Satz.
- **Offene Punkte.** Was bewusst nicht gemacht wurde.
- **Zeiger.** Datei-Pfade, Repos, URLs, Commit-SHAs. Pfade, keine Inhalte.

Raus bleibt: Gesprächsverlauf, Code-Dumps (der Code liegt im Repo), Selbstverständliches, alles was aus `git log` hervorgeht.

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/wrapup.py" \
  --title "Marketplace Setup" --project claude-plugins --tags "marketplace,plugins" <<'EOF'
## Entscheidungen
- Marketplace public statt privat, damit Fremde ohne Auth installieren

## Gotchas
- Version-Pin blockt Updates: ohne Bump zieht `plugin update` nichts

## Stand
- 4 Plugins live
EOF
```

Body kommt über stdin (oder `--content-file PATH`). Leerer Body → Exit 1, nichts geschrieben. Das Skript legt den Digest an und setzt die Index-Zeile oben ein.

`--title` wird zum Dateinamen (Umlaute werden transliteriert), `--project` und `--tags` machen `recall` filterbar. Beides optional, beides lohnt sich.

## Zurückholen (Session-Start oder bei Bedarf)

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/wrapup/scripts/recall.py" version pin update
```

Ausgabe: gerankte Digests mit Pfad und passenden Zeilen. **Dann erst** den relevanten Digest mit `Read` öffnen — nicht alle. Suchbegriffe werden alle kleingeschrieben; wer mehr Terme trifft, rankt höher.

Optionen: `--project <name>` grenzt auf ein Projekt ein, `--limit N` (Default 5) begrenzt die Treffer, `--context N` (Default 2) die Zeilen pro Treffer.

Kein Treffer → sag das und arbeite ohne. Erfinde nichts aus dem Gedächtnis, was nicht im Store steht.

Für „was hatten wir zuletzt" ohne konkreten Suchbegriff: `~/.claude/wrapup/INDEX.md` lesen — die Datei ist klein genug, um sie ganz zu laden.

## Optional: NotebookLM-Push

`--push-notebooklm` schickt denselben Digest zusätzlich als Notiz an NotebookLM (Gemini Notebook). Sinnvoll für dessen Medien-Features (Audio/Video-Overviews, Infografiken, Deep Research über die gesammelten Sessions) — **nicht** als Ersatz für den lokalen Store.

```bash
... | python ".../wrapup.py" --title "..." --push-notebooklm --notebook <id>
```

Ohne `--notebook` landet die Notiz im aktiven Notebook (`notebooklm use <id>`), oder setze `WRAPUP_NOTEBOOK`.

Voraussetzung: `notebooklm` CLI installiert und eingeloggt (`uv tool install notebooklm-py`, dann `notebooklm login`). Fehlt sie, meldet das Skript `skipped` und der lokale Digest ist trotzdem geschrieben — der Push kann den lokalen Pfad nie kaputt machen.

**Wichtig für die Erwartungshaltung:** `notebooklm-py` ist eine inoffizielle Bibliothek auf undokumentierten Google-Endpunkten. Google hat keine öffentliche NotebookLM-API (Stand 08/2026, nur Enterprise). Das kann jederzeit brechen. Genau deshalb ist der lokale Store die Basis und der Push die Kür — wer es andersherum baut, verliert bei der nächsten Google-Änderung sein Gedächtnis.

## Automatisch statt manuell

Der Skill triggert auf Zuruf. Wer den Digest **immer** am Session-Ende will, braucht einen `Stop`-Hook in `settings.json` — Hooks führt die Harness aus, nicht das Modell. Danach fragen, wenn der User das möchte; ungefragt keine Hooks installieren.
