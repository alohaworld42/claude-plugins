---
name: wrapup
description: Gedächtnis über Sessions hinweg — am Ende einer Session einen kompakten Digest speichern (Entscheidungen, Gotchas, Stand, offene Punkte), am Anfang der nächsten gezielt zurückholen statt Kontext neu aufzubauen. Lokal plus optionaler Notion-Spiegel. Nutzen wenn der User sagt "wrapup", "wrap up", "session speichern", "merk dir das für nächstes Mal", "was hatten wir letztes Mal", "worauf sind wir stehengeblieben", "erinnerst du dich an", eine Session abschließt, oder nach früheren Entscheidungen/Fixes fragt.
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

## Optional: Notion-Spiegel (empfohlener Zweitspeicher)

Wer Notion nutzt, bekommt damit Volltext-/Semantiksuche über alle Sessions, Zugriff vom Handy und strukturierte Filter — über die **offizielle** Notion-API und den offiziellen MCP-Server. Kein Browser-Hack, keine undokumentierten Endpunkte.

Ablauf nach dem lokalen Schreiben (der lokale Digest ist immer die Basis):

1. **Datenbank finden.** Cache lesen: `~/.claude/wrapup/notion.json` (`{"data_source_id": "..."}`). Fehlt die Datei → mit `notion-search` nach einer Datenbank „Claude Session Log" suchen, `data_source_id` in den Cache schreiben.
2. **Fehlt sie ganz**, dem User anbieten sie anzulegen (nicht ungefragt) — `notion-create-database`:
   ```
   CREATE TABLE ("Titel" TITLE, "Datum" DATE,
                 "Projekt" SELECT('sonstiges':gray),
                 "Tags" MULTI_SELECT('memory':purple, 'gotcha':red, 'entscheidung':blue, 'setup':gray),
                 "Stand" RICH_TEXT COMMENT 'Ein Satz: wo die Sache steht')
   ```
3. **Push** mit `notion-create-pages`, `parent = {type: "data_source_id", data_source_id: <id>}`. Properties `Titel`/`Datum`/`Projekt`/`Tags`/`Stand` setzen, Digest-Body als `content` (Markdown, ohne Titel-Überschrift — der Titel steckt in den Properties).

Der Push läuft agent-seitig über MCP, nicht im Skript: Ein Digest ist eine Synthese der Session — die kann nur das Modell erzeugen, kein Skript und kein Hook.

### Recall aus Notion

Zwei Wege, beide verifiziert:

- **`notion-search`** mit normaler Suchanfrage — findet Digests workspace-weit inklusive Trefferzeile. Der schnelle Standardweg.
- **`notion-query-data-sources`** (SQL) für strukturierte Fragen — „alle Sessions zu Projekt X, neueste zuerst":
  ```sql
  SELECT "Titel", "date:Datum:start" AS Datum, "Stand", url
  FROM "collection://<data_source_id>"
  WHERE "Projekt" = ? ORDER BY "date:Datum:start" DESC LIMIT 5
  ```

Gotcha: `notion-search` mit `data_source_url` (semantische Suche innerhalb der DB) lieferte direkt nach dem Anlegen einer Seite **leer** zurück — der Index braucht Zeit. Workspace-Suche und SQL-Query greifen sofort. Bei frischen Digests also nicht auf `data_source_url` setzen.

## Alternative: NotebookLM

`--push-notebooklm` schickt den Digest stattdessen als Notiz an NotebookLM (Gemini Notebook) — interessant nur wegen dessen Medien-Features (Audio/Video-Overviews, Infografiken).

```bash
... | python ".../wrapup.py" --title "..." --push-notebooklm --notebook <id>
```

Voraussetzung: `notebooklm` CLI installiert und eingeloggt (`uv tool install notebooklm-py`, dann `notebooklm login`). Ohne `--notebook` gilt das aktive Notebook, oder setze `WRAPUP_NOTEBOOK`. Fehlt die CLI, meldet das Skript `skipped` und der lokale Digest steht trotzdem.

**Erwartungshaltung:** `notebooklm-py` läuft auf undokumentierten Google-Endpunkten; eine öffentliche NotebookLM-API gibt es nicht (Stand 08/2026, nur Enterprise). Kann jederzeit brechen. Wer Notion hat, nimmt Notion.

**Grundregel für beide:** lokaler Store ist die Basis, der Spiegel ist die Kür. Ein externer Dienst darf nie das einzige Gedächtnis sein — sonst ist es weg, wenn der Anbieter etwas ändert.

## Automatisch statt manuell

Der Skill triggert auf Zuruf. Wer den Digest **immer** am Session-Ende will, braucht einen `Stop`-Hook in `settings.json` — Hooks führt die Harness aus, nicht das Modell. Danach fragen, wenn der User das möchte; ungefragt keine Hooks installieren.
