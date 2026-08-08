# telegramm

Erklärt: wofür der Skill da ist, wie er getestet wurde, wie effizient er ist.

## Zweck

Jedes ausgegebene Wort kostet doppelt: Lesezeit des Users UND Tokens — gleicher Hebel, weniger Wörter senkt beides. `telegramm` erzwingt Ergebnis-zuerst, Telegrammstil, Symbole statt Prosa, hartes Zeilenbudget für Status-Updates und Endnachrichten.

Kürzen passiert durch **Auswahl vor dem Schreiben**, nicht durch Fremdsprach-Kompression (kein Mandarin-Trick) und nicht durch Schreiben-dann-Streichen — verworfene Zeilen sind bereits bezahlte Tokens. Details: [SKILL.md](skills/telegramm/SKILL.md).

## Sub-Agents (ab 1.1.0)

Sub-Agents starten mit eigenem Kontext, in dem der Skill nicht geladen ist — ihre Rückgaben kamen deshalb weiterhin als Fließtext zurück und blähten die Endnachricht des Haupt-Agents auf. Seit 1.1.0 enthält der Skill einen Format-Block, den der Haupt-Agent an jeden Sub-Agent-Prompt anhängt, plus die Regel, Sub-Agent-Ergebnisse zu verdichten statt durchzureichen.

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

## Ergebnisse (Iteration 3, 2026-08-08) — Retest: Token-Ersparnis, Symbole, Englisch

Neuer Lauf mit 3 Konfigurationen (Baseline ohne Skill · Skill mit Symbolen · Skill-Variante ohne Symbole, Status als Wörter) auf 2 Aufgaben, jeweils Sonnet-Subagent, identischer Task-Prompt. Getestet wurde der Sub-Agent-Format-Block aus 1.1.0 — das ist der Teil des Skills, der in der Praxis an Sub-Agent-Prompts angehängt wird.

**Token-Ersparnis** (Wörter / Zeichen der Rückgabe; Tokens ≈ Zeichen ÷ 3):

| Aufgabe | Baseline | Skill mit Symbolen | Skill ohne Symbole |
|---|---|---|---|
| T1 Bug-Fix-Report (Deutsch) | 73 W / 633 Z | 31 W / 377 Z (**−58% / −40%**) | 52 W / 514 Z (−29% / −19%) |
| T2 Crash-Log-Analyse (Englisch) | 379 W / 2 619 Z | 85 W / 740 Z (**−78% / −72%**) | 111 W / 809 Z (−71% / −69%) |

Inhaltlich kein Verlust: alle Läufe fanden den Off-by-one-Bug (und fixten ihn korrekt in der Datei) bzw. die OOM-Ursache (unbegrenztes Cache-Wachstum) samt Fix und Restrisiko.

**Sind Symbole nötig?** Ja — behalten. Die Variante ohne Symbole war durchgehend länger (T1: +36% Zeichen, T2: +9%) und produzierte mehr Füll-Zeilen („Status: … erledigt; … offen"). Symbole sparen nicht nur die ersetzten Wörter (`✓` vs. „erledigt und gefixt"), sie disziplinieren auch die Struktur: eine Markierung pro Zeile statt Prosa-Ansätze. Der Effekt ist bei kurzen Antworten am größten.

**Funktioniert der Skill auf Englisch?** Nach einem Fix: ja. Der Retest reproduzierte den Sprach-Bug aus Iteration 1 an neuer Stelle — der **deutsche** Format-Block aus 1.1.0 zog englische Tasks auf Deutsch (beide Skill-Varianten antworteten deutsch auf einen englischen Prompt; die Zeile „Ausgabesprache = Sprache dieses Prompts" reichte nicht, weil der Block selbst Teil des Prompts ist). Fix in 1.2.0: der Block wird in der **Sprache des Task-Prompts** angehängt, englische Fassung liegt fertig im Skill. Re-Test verifiziert: Antwort vollständig englisch, 10 Zeilen, Format eingehalten, −69% Wörter gegen Baseline.

## Propagations-Test (Iteration 3b, 2026-08-08)

Getestet wurde zusätzlich, ob ein Haupt-Agent mit geladenem Skill die Sub-Agent-Regel wirklich **befolgt** (nicht nur, ob der Block wirkt): 2 Haupt-Agenten (Sonnet) bekamen SKILL.md als aktiven Skill und mussten eine Log-Analyse an einen eigenen Sub-Agent delegieren; geprüft wurde der exakte weitergereichte Prompt.

| Test | Block angehängt? | Block-Sprache korrekt? | Rückgabe verdichtet statt durchgereicht? |
|---|---|---|---|
| Haupt-Agent deutsch | ✓ wortgleich | ✓ deutsch | ✓ 10 → 5 Zeilen |
| Haupt-Agent englisch | ✓ wortgleich | ✓ englisch (neue 1.2.0-Regel) | ✓ |

Gefundene Lücke: Der Block band nur die erste Ebene — ein Sub-Agent, der selbst Sub-Agents startet, reichte ihn nicht weiter. Fix: Block enthält jetzt eine Weiterreich-Zeile („Startest du selbst Sub-Agents: diesen Block an deren Prompts anhängen"), Propagation ist damit transitiv.

Nicht von innen testbar bleibt das **Triggern** des Skills im Hauptchat (Description-Matching durch den Harness bei „kurz", „tldr" etc.) — das entscheidet die Plattform, nicht der Skill-Inhalt.

## Grenzen

- `runs_per_configuration: 1` — schnelle Validierung, kein groß angelegtes Benchmark mit Streuung (stddev). Gilt auch für Iteration 3.
- Baseline = Sonnet-Subagent mit `effort: low`, von Haus aus knapper als ein Standard-Assistent ohne Skill — reale Ersparnis im Alltag vermutlich höher als hier gemessen.
- Rohdaten (Fixtures, `benchmark.json`, Reports pro Lauf) liegen in `~/.claude/skills/telegramm-workspace/iteration-1/` — nicht Teil dieses Repos.
