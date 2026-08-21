<#
.SYNOPSIS
    Installiert das always-on Profil (stfu, telegramm, research-first, tool-routing,
    capability-reminder) als Hooks in Claude Code.
.DESCRIPTION
    Kopiert die Inject-Dateien nach ~/.claude/, legt einen einzelnen Profil-Hook an,
    der die aktiven Module zusammensetzt, und mergt die Hook-Eintraege in settings.json.
    Bestehende Einstellungen UND bestehende Fremd-Hooks (z. B. caveman) bleiben erhalten.
    Idempotent -- kann mehrfach ausgefuehrt werden.
.NOTES
    Ausfuehren: .\install-hooks.ps1
    Modul aus:  New-Item ~/.claude/telegramm-off      (analog: stfu-off, research-first-off, tools-off)
    Modul an:   Remove-Item ~/.claude/telegramm-off
    Alles aus:  New-Item ~/.claude/profile-off
#>

$ErrorActionPreference = 'Stop'
$claudeDir = Join-Path $HOME '.claude'
$settingsPath = Join-Path $claudeDir 'settings.json'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$hooksSourceDir = Join-Path $scriptDir 'hooks'

# Reihenfolge = Reihenfolge im injizierten Block: erst Methode, dann Routing, dann Stil.
$modules = @('research-first', 'tools', 'stfu', 'telegramm')

# --- 1. ~/.claude/ sicherstellen ---
if (-not (Test-Path $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
    Write-Host "[+] $claudeDir angelegt"
}

# --- 2. Inject-Dateien kopieren ---
$files = @('capability-reminder.txt') + ($modules | ForEach-Object { "$_-inject.txt" })
foreach ($f in $files) {
    $src = Join-Path $hooksSourceDir $f
    if (-not (Test-Path $src)) { Write-Host "[!] fehlt, uebersprungen: $f"; continue }
    Copy-Item -Path $src -Destination (Join-Path $claudeDir $f) -Force
    Write-Host "[+] $f -> $claudeDir"
}

# --- 3. Profil-Hook erzeugen (ein Hook, Module einzeln abschaltbar) ---
$profileHook = Join-Path $claudeDir 'profile-hook.ps1'
$moduleList = ($modules | ForEach-Object { "'$_'" }) -join ','
@"
`$c = Join-Path `$HOME '.claude'
if (Test-Path (Join-Path `$c 'profile-off')) { exit 0 }
foreach (`$m in @($moduleList)) {
    if (Test-Path (Join-Path `$c "`$m-off")) { continue }
    `$f = Join-Path `$c "`$m-inject.txt"
    if (Test-Path `$f) { Get-Content `$f -Encoding UTF8 }
}
"@ | Set-Content -Path $profileHook -Encoding UTF8
Write-Host "[+] profile-hook.ps1 erstellt ($($modules -join ', '))"

# --- 4. settings.json mergen ---
$capFile = (Join-Path $claudeDir 'capability-reminder.txt') -replace '\\', '/'
$profileHookPath = $profileHook -replace '\\', '/'

$sessionCmd = "powershell -NoProfile -Command `"Get-Content '$capFile' -Encoding UTF8`""
$promptCmd  = "powershell -NoProfile -File `"$profileHookPath`""

# PSObject -> Hashtable, rekursiv. Ersetzt ConvertFrom-Json -AsHashtable,
# das erst ab PowerShell 6 existiert (Windows-Standard ist 5.1).
function ConvertTo-HashtableRecursive {
    param($InputObject)
    if ($null -eq $InputObject) { return $null }
    if ($InputObject -is [System.Collections.IEnumerable] -and $InputObject -isnot [string]) {
        return @( foreach ($item in $InputObject) { ConvertTo-HashtableRecursive $item } )
    }
    if ($InputObject -is [PSCustomObject]) {
        $ht = @{}
        foreach ($prop in $InputObject.PSObject.Properties) {
            $ht[$prop.Name] = ConvertTo-HashtableRecursive $prop.Value
        }
        return $ht
    }
    return $InputObject
}

# Fremde Hook-Gruppen behalten, eigene ersetzen (idempotent statt doppelt).
# Jede Gruppe wird neu aufgebaut, damit 'hooks' garantiert ein Array bleibt --
# ein einzelnes Objekt an dieser Stelle passt nicht zum Hook-Schema.
function Merge-HookGroup {
    param($Existing, [string]$Command, [string]$Marker)
    $kept = @()
    foreach ($group in @($Existing)) {
        if ($null -eq $group) { continue }
        $inner = @($group['hooks'])
        $isOurs = $false
        foreach ($h in $inner) {
            if ($h -and "$($h['command'])" -like "*$Marker*") { $isOurs = $true }
        }
        if (-not $isOurs) {
            $rebuilt = @{}
            foreach ($k in $group.Keys) { $rebuilt[$k] = $group[$k] }
            $rebuilt['hooks'] = $inner
            $kept += $rebuilt
        }
    }
    # Komma-Operator: sonst rollt PowerShell ein einelementiges Array beim return aus.
    return , @($kept + @{ hooks = @(@{ type = 'command'; command = $Command }) })
}

if (Test-Path $settingsPath) {
    Copy-Item $settingsPath "$settingsPath.bak" -Force
    $existing = ConvertTo-HashtableRecursive (Get-Content $settingsPath -Raw | ConvertFrom-Json)
    if ($null -eq $existing) { $existing = @{} }
    Write-Host "[i] Bestehende settings.json gefunden -- merge (Backup: settings.json.bak)"
} else {
    $existing = @{}
    Write-Host "[i] Keine settings.json vorhanden -- neu anlegen"
}

if (-not $existing.ContainsKey('hooks') -or $null -eq $existing['hooks']) { $existing['hooks'] = @{} }
$hooks = $existing['hooks']

$hooks['SessionStart']     = Merge-HookGroup $hooks['SessionStart']     $sessionCmd 'capability-reminder.txt'
$hooks['UserPromptSubmit'] = Merge-HookGroup $hooks['UserPromptSubmit'] $promptCmd  'profile-hook.ps1'
$existing['hooks'] = $hooks

# ConvertTo-Json in PowerShell 5.1 klappt einelementige Arrays zu Objekten zusammen --
# das zerstoert das Hook-Schema (hooks: [...] wuerde zu hooks: {...}).
# JavaScriptSerializer haelt Arrays als Arrays.
Add-Type -AssemblyName System.Web.Extensions
$serializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$serializer.MaxJsonLength = [int]::MaxValue
$json = $serializer.Serialize($existing)
Set-Content -Path $settingsPath -Value $json -Encoding UTF8
Write-Host "[+] settings.json aktualisiert: $settingsPath"

# --- 4b. Verifizieren, dass die Hooks wirklich in der Datei stehen ---
$check = Get-Content $settingsPath -Raw | ConvertFrom-Json
$hasSession = ($check.hooks.SessionStart | Out-String) -like '*capability-reminder*'
$hasPrompt  = ($check.hooks.UserPromptSubmit | Out-String) -like '*profile-hook*'
if ($hasSession -and $hasPrompt) {
    Write-Host "[OK] Hooks verifiziert in settings.json"
} else {
    Write-Host "[FEHLER] Hooks NICHT in settings.json gelandet -- bitte Datei pruefen: $settingsPath" -ForegroundColor Red
    exit 1
}

# --- 5. Zusammenfassung ---
Write-Host ''
Write-Host '=== Installation abgeschlossen ==='
Write-Host 'Aktive Hooks:'
Write-Host '  SessionStart     -> capability-reminder (Faehigkeiten-Check)'
Write-Host "  UserPromptSubmit -> profile-hook ($($modules -join ' + '))"
Write-Host ''
Write-Host 'Toggle (Datei anlegen = aus, loeschen = an):'
foreach ($m in $modules) { Write-Host "  New-Item ~/.claude/$m-off" }
Write-Host '  New-Item ~/.claude/profile-off   # alles auf einmal aus'
Write-Host ''
Write-Host 'Neuen Claude-Code-Chat starten, damit die Hooks greifen.'
Write-Host ''
Write-Host 'WO HOOKS LAUFEN:'
Write-Host '  Claude Code CLI      : ja'
Write-Host '  Claude Desktop-App   : ja'
Write-Host '  VS-Code-Erweiterung  : ja (2026-08 geprueft -- UserPromptSubmit feuert;'
Write-Host '                         Issue #21736 galt fuer aeltere Versionen)'
Write-Host '  Fallback ueberall    : ~/.claude/CLAUDE.md haelt dasselbe Profil als Text'
Write-Host ''
Write-Host 'Pruefen: /hooks im Chat zeigt aktive Hooks. Trace: claude --debug-file trace.log'
