# telegramm

Erklärt: wofür der Skill da ist, wie er getestet wurde, wie effizient er ist.

## Zweck

Jedes ausgegebene Wort kostet doppelt: Lesezeit des Users UND Tokens — gleicher Hebel, weniger Wörter senkt beides. `telegramm` erzwingt Ergebnis-zuerst, Telegrammstil, Symbole statt Prosa, hartes Zeilenbudget für Status-Updates und Endnachrichten.

Kürzen passiert durch **Auswahl vor dem Schreiben**, nicht durch Fremdsprach-Kompression (kein Mandarin-Trick) und nicht durch Schreiben-dann-Streichen — verworfene Zeilen sind bereits bezahlte Tokens. Details: [SKILL.md](skills/telegramm/SKILL.md).

## Eval-Methodik

3 Testfälle, je ein Subagent **mit** Skill gegen einen Baseline-Subagent **ohne** Skill, identischer Prompt, gleiches Modell (Sonnet, low effort):

| Eval | Aufgabe | Sprache |
|---|---|---|
| `eval-0-debug-report` | Bug in `calc.js` finden + fixen + berichten | Deutsch |
| `eval-1-multistep-status` | Mini-Node-Projekt anlegen, Fortschritt melden | Deutsch |
| `eval-2-log-analysis` | Crash-Log lesen, Ursache + Fix berichten | Englisch |

Fixtures unter `fixtures/` (Repo mit dem Eval-Workspace, nicht Teil des Plugins). Assertions pro Fall geprüft (Inhalt korrekt? Format eingehalten?), aggregiert in `benchmark.json`.

## Ergebnisse (Iteration 1, 2026-08-05)

| Eval | Wörter mit Skill | Wörter ohne | Δ | Pass mit | Pass ohne |
|---|---|---|---|---|---|
| eval-0 | 39 | 48 | −19% | 4/4 | 4/4 |
| eval-1 | 29 | 53 | −45% | 5/5 | 4/5 |
| eval-2 | 58 | 251 | **−77%** | 5/6 | 5/6 |

Ersparnis wächst mit Task-Größe/Baseline-Länge. Kein Informationsverlust bei den Inhalts-Assertions (Ursache, Fix, nächster Schritt — überall vorhanden).

**Gefundener Bug:** eval-2 mit Skill antwortete auf Deutsch, obwohl der User-Prompt Englisch war — die deutsche Skill-Sprache hatte die Sprachwahl überschrieben. Fix: explizite Regel „Ausgabesprache = Sprache der letzten User-Nachricht" + englisches Beispiel im Skill. Danach re-verifiziert.

**Iteration 2** (Regel „Tokens nie erzeugen statt streichen" nachgeschärft): Retest von eval-1 zeigt weitere Verdichtung — Status-Updates 2→0, Endnachricht 29→~20 Wörter, gleicher Informationsgehalt.

## Grenzen

- `runs_per_configuration: 1` — schnelle Validierung, kein groß angelegtes Benchmark mit Streuung (stddev).
- Baseline = Sonnet-Subagent mit `effort: low`, von Haus aus knapper als ein Standard-Assistent ohne Skill — reale Ersparnis im Alltag vermutlich höher als hier gemessen.
- Rohdaten (Fixtures, `benchmark.json`, Reports pro Lauf) liegen in `~/.claude/skills/telegramm-workspace/iteration-1/` — nicht Teil dieses Repos.
