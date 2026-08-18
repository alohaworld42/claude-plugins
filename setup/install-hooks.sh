#!/usr/bin/env bash
set -euo pipefail

# Installiert die always-on Hooks (telegramm, stfu, capabilities) in Claude Code.
# Kopiert Inject-Dateien nach ~/.claude/ und mergt die Hook-Einträge in settings.json.
# Bestehende Einstellungen (Permissions etc.) bleiben erhalten. Idempotent.
#
# Deaktivieren einzelner Hooks: touch ~/.claude/telegramm-off  (oder stfu-off)
# Reaktivieren: rm ~/.claude/telegramm-off

CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_SRC="$SCRIPT_DIR/hooks"

mkdir -p "$CLAUDE_DIR"

# --- 1. Inject-Dateien kopieren ---
for f in telegramm-inject.txt stfu-inject.txt capability-reminder.txt; do
  cp "$HOOKS_SRC/$f" "$CLAUDE_DIR/$f"
  echo "[+] $f -> $CLAUDE_DIR"
done

# --- 2. Hook-Skripte erstellen ---
cat > "$CLAUDE_DIR/telegramm-hook.sh" << 'HOOK'
#!/usr/bin/env bash
[ -f "$HOME/.claude/telegramm-off" ] && exit 0
cat "$HOME/.claude/telegramm-inject.txt"
HOOK
chmod +x "$CLAUDE_DIR/telegramm-hook.sh"
echo "[+] telegramm-hook.sh erstellt"

cat > "$CLAUDE_DIR/stfu-hook.sh" << 'HOOK'
#!/usr/bin/env bash
[ -f "$HOME/.claude/stfu-off" ] && exit 0
cat "$HOME/.claude/stfu-inject.txt"
HOOK
chmod +x "$CLAUDE_DIR/stfu-hook.sh"
echo "[+] stfu-hook.sh erstellt"

# --- 3. settings.json mergen ---
HOOKS_JSON=$(cat << 'JSON'
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "cat ~/.claude/capability-reminder.txt"
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "~/.claude/telegramm-hook.sh"
        },
        {
          "type": "command",
          "command": "~/.claude/stfu-hook.sh"
        }
      ]
    }
  ]
}
JSON
)

if [ -f "$SETTINGS" ]; then
  echo "[i] Bestehende settings.json gefunden — merge"
  if command -v jq &>/dev/null; then
    jq --argjson hooks "$HOOKS_JSON" '.hooks = $hooks' "$SETTINGS" > "$SETTINGS.tmp"
    mv "$SETTINGS.tmp" "$SETTINGS"
  else
    echo "[!] jq nicht installiert — settings.json wird überschrieben (nur hooks-Block)"
    echo "{\"hooks\": $HOOKS_JSON}" > "$SETTINGS"
  fi
else
  echo "[i] Keine settings.json vorhanden — neu anlegen"
  echo "{\"hooks\": $HOOKS_JSON}" > "$SETTINGS"
fi
echo "[+] settings.json aktualisiert: $SETTINGS"

echo ''
echo '=== Installation abgeschlossen ==='
echo 'Aktive Hooks:'
echo '  SessionStart     -> capability-reminder (Faehigkeiten-Check)'
echo '  UserPromptSubmit -> telegramm-hook + stfu-hook'
echo ''
echo 'Toggle:'
echo '  Telegramm aus:  touch ~/.claude/telegramm-off'
echo '  Telegramm an:   rm ~/.claude/telegramm-off'
echo '  STFU aus:       touch ~/.claude/stfu-off'
echo '  STFU an:        rm ~/.claude/stfu-off'
echo ''
echo 'Neuen Claude-Code-Chat starten, damit die Hooks greifen.'
