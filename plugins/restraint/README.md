# restraint

Vier Grenzen gegen die Eagerness eines Agents. Schlechte Outputs sind selten
eine Wissenslücke — sie sind Übereifer: Dateien umgeschrieben, die niemand
nannte; geraten statt gefragt; ein System gebaut für einen Einzeiler. Eifer
lässt sich nicht durch *mehr* Anweisungen fixen, nur durch Weglassen.

## Die vier Grenzen

1. **Weniger schreiben** — kleinster Output, der die Aufgabe voll erfüllt. Keine ungefragte Fehlerbehandlung, Config, Generalität.
2. **Nur das Verlangte** — der Prompt ist der Scope, kein Startpunkt zum Ausweiten. Bestehenden Stil spiegeln; nur eigene verwaiste Imports aufräumen, fremden Dead Code nennen statt löschen.
3. **Prüfen vor „fertig"** — „done" ist eine Behauptung, die stimmen muss. Vage Aufgaben vorher in verifizierbare umformen („Fix bug" → Test der ihn reproduziert, dann grün).
4. **Fragen statt raten** — bei echter Mehrdeutigkeit eine scharfe Frage. Interpretationen vorlegen statt still wählen, Widerspruch einlegen wenn einfacher geht, Verwirrung benennen.

**Tradeoff:** Vorsicht vor Tempo. Bei trivialen Aufgaben Urteilsvermögen nutzen — Restraint ist keine Lähmung.

## Abgrenzung zu `stfu`

`stfu` = kein Kommentar, keine ungefragte Meinung (Ton). `restraint` = kein
ungefragter Scope, kein Übererfüllen (Umfang). Ergänzen sich.

## Trigger

„restraint", „stop being eager", „don't over-engineer", „follow the prompt",
„don't touch what I didn't ask for", „stop guessing".

## Herkunft

- Konzept „one file, four boundaries" aus einem Instagram-Reel von [@jackroberts___](https://www.instagram.com/p/DcOwUcySo8w/) zu Prompt-Disziplin bei Claude.
- Push-back-, Surgical-Change- und Goal-Driven-Regeln (v1.1.0) übernommen aus [karpathy-guidelines](https://github.com/multica-ai/andrej-karpathy-skills) (MIT, forrestchang) — abgeleitet aus [Andrej Karpathys Beobachtungen](https://x.com/karpathy/status/2015883857489522876) zu LLM-Coding-Fallstricken.

## Installation

```
/plugin install restraint@alohaworld-plugins
```
