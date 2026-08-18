<#
.SYNOPSIS
    Installiert die always-on Hooks (telegramm, stfu, capabilities) in Claude Code.
.DESCRIPTION
    Kopiert Inject-Dateien nach ~/.claude/ und mergt die Hook-Einträge in settings.json.
    Bestehende Einstellungen (Permissions etc.) bleiben erhalten.
    Idempotent — kann mehrfach ausgeführt werden.
.NOTES
    Ausführen: .\install-hooks.ps1
    Deaktivieren einzelner Hooks: New-Item ~/.claude/telegramm-off  (oder stfu-off)
    Reaktivieren: Remove-Item ~/.claude/telegramm-off
#>

$ErrorActionPreference = 'Stop'
$claudeDir = Join-Path $HOME '.claude'
$settingsPath = Join-Path $claudeDir 'settings.json'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$hooksSourceDir = Join-Path $scriptDir 'hooks'

# --- 1. ~/.claude/ sicherstellen ---
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    Write-Host "[+] $claudeDir angelegt"
}

# --- 2. Inject-Dateien kopieren ---
$files = @('telegramm-inject.txt', 'stfu-inject.txt', 'capability-reminder.txt')
foreach ($f in $files) {
    $src = Join-Path $hooksSourceDir $f
    $dst = Join-Path $claudeDir $f
    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "[+] $f -> $claudeDir"
}

# --- 3. Hook-Skripte erstellen (PowerShell-kompatibel) ---

# telegramm-hook
$telegrammHook = Join-Path $claudeDir 'telegramm-hook.ps1'
@'
if (Test-Path (Join-Path $HOME '.claude' 'telegramm-off')) { exit 0 }
Get-Content (Join-Path $HOME '.claude' 'telegramm-inject.txt')
'@ | Set-Content -Path $telegrammHook -Encoding UTF8
Write-Host "[+] telegramm-hook.ps1 erstellt"

# stfu-hook
$stfuHook = Join-Path $claudeDir 'stfu-hook.ps1'
@'
if (Test-Path (Join-Path $HOME '.claude' 'stfu-off')) { exit 0 }
Get-Content (Join-Path $HOME '.claude' 'stfu-inject.txt')
'@ | Set-Content -Path $stfuHook -Encoding UTF8
Write-Host "[+] stfu-hook.ps1 erstellt"

# --- 4. settings.json mergen ---
$capFile = (Join-Path $claudeDir 'capability-reminder.txt') -replace '\\', '/'
$telegrammHookPath = ($telegrammHook) -replace '\\', '/'
$stfuHookPath = ($stfuHook) -replace '\\', '/'

$newHooks = @{
    hooks = @{
        SessionStart = @(
            @{
                hooks = @(
                    @{
                        type    = 'command'
                        command = "powershell -NoProfile -Command `"Get-Content '$capFile'`""
                    }
                )
            }
        )
        UserPromptSubmit = @(
            @{
                hooks = @(
                    @{
                        type    = 'command'
                        command = "powershell -NoProfile -File `"$telegrammHookPath`""
                    },
                    @{
                        type    = 'command'
                        command = "powershell -NoProfile -File `"$stfuHookPath`""
                    }
                )
            }
        )
    }
}

if (Test-Path $settingsPath) {
    $existing = Get-Content $settingsPath -Raw | ConvertFrom-Json -AsHashtable
    Write-Host "[i] Bestehende settings.json gefunden — merge"
} else {
    $existing = @{}
    Write-Host "[i] Keine settings.json vorhanden — neu anlegen"
}

$existing['hooks'] = $newHooks.hooks

$json = $existing | ConvertTo-Json -Depth 10
Set-Content -Path $settingsPath -Value $json -Encoding UTF8
Write-Host "[+] settings.json aktualisiert: $settingsPath"

# --- 5. Zusammenfassung ---
Write-Host ''
Write-Host '=== Installation abgeschlossen ==='
Write-Host 'Aktive Hooks:'
Write-Host '  SessionStart    -> capability-reminder (Faehigkeiten-Check)'
Write-Host '  UserPromptSubmit -> telegramm-hook + stfu-hook'
Write-Host ''
Write-Host 'Toggle:'
Write-Host '  Telegramm aus:  New-Item ~/.claude/telegramm-off'
Write-Host '  Telegramm an:   Remove-Item ~/.claude/telegramm-off'
Write-Host '  STFU aus:       New-Item ~/.claude/stfu-off'
Write-Host '  STFU an:        Remove-Item ~/.claude/stfu-off'
Write-Host ''
Write-Host 'Neuen Claude-Code-Chat starten, damit die Hooks greifen.'
