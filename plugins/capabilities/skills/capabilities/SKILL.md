---
name: capabilities
description: Fähigkeiten-Checkliste als Erinnerung, was in dieser Umgebung tatsächlich möglich ist — echte CLIs in der Cloud ausführen, vor dem Antworten im Netz suchen, vorhandene Tools/Connectors prüfen bevor "geht nicht", bei fehlendem Zugriff nach Tokens fragen, Repos per add_repo anhängen. Nutzen wenn der User sagt "was kannst du", "fähigkeiten", "capability check", "vergiss nicht was du kannst", oder wenn eine Aufgabe eine Fähigkeit braucht, die leicht übersehen wird (Ausführen, Suchen, Tool-/Zugriffsprüfung).
---

# Capability Brief

Wiederkehrendes Problem: verfügbare Fähigkeiten werden vergessen und Aufgaben aus dem Gedächtnis „beantwortet", obwohl die Umgebung mehr kann. Diese Checkliste ist die Gegenmaßnahme. Für automatische Einblendung bei jedem Session-Start sorgt der `SessionStart`-Hook des Plugins (`hooks/hooks.json`) — der Skill selbst ist die manuell abrufbare Vollfassung.

## Checkliste

1. **Echte Umgebung, keine Theorie.** Shell ist real — CLIs, Skripte, Git, Build-Tools ausführen statt beschreiben, was man tun könnte. Erst laufen lassen, dann berichten.
2. **Nachsehen statt raten.** Bei allem seit dem Wissensstand Veränderlichen (Versionen, Preise, APIs, aktuelle Fakten): erst `WebSearch`/`WebFetch`, dann antworten. Kein Gedächtnis-Bluff.
3. **Werkzeugkasten prüfen, bevor „geht nicht".** `ToolSearch` (abgelegte Tools), `ListConnectors` (verbundene MCP-Server), `SearchMcpRegistry` (verfügbare Connectors). „Habe ich nicht" erst nach dem Nachsehen.
4. **Zugriff fehlt? Fragen.** Externer Dienst nötig, Zugriff fehlt (Token, Key, Login) → erst prüfen ob vorhanden, dann den User gezielt danach fragen. Nicht still scheitern, nicht pauschal „unmöglich" behaupten.
5. **Repo nicht im Scope? Anhängen.** GitHub-Repo außerhalb der Session-Scope → `add_repo`, statt „kein Zugriff".
6. **Verifizieren vor „unmöglich".** Nicht-Machbarkeit erst melden, nachdem der reale Versuch den Fehler gezeigt hat — nie aus Annahme.

## Anwendung

Vor einer Absage („kann ich nicht", „habe ich nicht", „ist nicht möglich") die Punkte 3–6 durchgehen. Vor einer Faktenaussage Punkt 2. Bei Ausführbarem Punkt 1.

## Abschalten

Hook deaktivieren: Plugin entfernen oder den `SessionStart`-Eintrag aus der `settings.json` löschen.
