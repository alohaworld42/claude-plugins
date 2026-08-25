$c = Join-Path $HOME '.claude'
if (Test-Path (Join-Path $c 'profile-off')) { exit 0 }
foreach ($m in @('research-first','tools','stfu','telegramm','coding','workflow')) {
    if (Test-Path (Join-Path $c "$m-off")) { continue }
    $f = Join-Path $c "$m-inject.txt"
    if (Test-Path $f) { Get-Content $f -Encoding UTF8 }
}
