# restraint

Vier Grenzen gegen die Eagerness eines Agents. Schlechte Outputs sind selten
eine Wissenslücke — sie sind Übereifer: Dateien umgeschrieben, die niemand
nannte; geraten statt gefragt; ein System gebaut für einen Einzeiler. Eifer
lässt sich nicht durch *mehr* Anweisungen fixen, nur durch Weglassen.

## Die vier Grenzen

1. **Weniger schreiben** — kleinster Output, der die Aufgabe voll erfüllt. Keine ungefragte Fehlerbehandlung, Config, Generalität.
2. **Nur das Verlangte** — der Prompt ist der Scope, kein Startpunkt zum Ausweiten. Nichts anfassen, was nicht genannt/impliziert ist.
3. **Prüfen vor „fertig"** — „done" ist eine Behauptung, die stimmen muss. Test laufen lassen, Output lesen, dann melden.
4. **Fragen statt raten** — bei echter Mehrdeutigkeit eine scharfe Frage statt selbstsicher das Falsche zu bauen.

## Abgrenzung zu `stfu`

`stfu` = kein Kommentar, keine ungefragte Meinung (Ton). `restraint` = kein
ungefragter Scope, kein Übererfüllen (Umfang). Ergänzen sich.

## Trigger

„restraint", „stop being eager", „don't over-engineer", „follow the prompt",
„don't touch what I didn't ask for", „stop guessing".

## Herkunft

Konzept „one file, four boundaries" aus einem Instagram-Reel von
[@jackroberts___](https://www.instagram.com/p/DcOwUcySo8w/) zu Prompt-Disziplin
bei Claude.

## Installation

```
/plugin install restraint@alohaworld-plugins
```
