# capabilities

Blendet zu Session-Start eine Fähigkeiten-Checkliste ein — gegen das Vergessen dessen, was die Umgebung tatsächlich kann.

## Zweck

Wiederkehrendes Muster: verfügbare Fähigkeiten werden übersehen und Aufgaben aus dem Gedächtnis beantwortet, statt die Umgebung zu nutzen. Dieses Plugin erinnert bei jedem Session-Start an sechs Punkte:

1. Echte CLIs in der Cloud ausführen statt beschreiben
2. Vor dem Antworten im Netz suchen (veränderliche Fakten)
3. Vorhandene Tools/Connectors prüfen, bevor „geht nicht"
4. Bei fehlendem Zugriff nach Tokens/Keys fragen
5. Repos außerhalb der Scope per `add_repo` anhängen
6. Vor „unmöglich" den realen Versuch machen

## Mechanik

- `hooks/hooks.json` — `SessionStart`-Hook, der `reminder.txt` bei jedem Start als Kontext einblendet (Hooks führt die Harness aus, nicht das Modell — nur so feuert es automatisch).
- `skills/capabilities/SKILL.md` — manuell abrufbare Vollfassung („capability check").

Ein Skill allein triggert nur auf Stichworte; die automatische Einblendung leistet der Hook.

## Installation

```
/plugin install capabilities@alohaworld-plugins
```

Alternativ ohne Plugin-System (z. B. Remote-Session): den `SessionStart`-Hook direkt in `~/.claude/settings.json` eintragen und auf eine lokale Kopie von `reminder.txt` zeigen lassen.
