$DEST = Join-Path $HOME ".gemini\config"
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "=== Installing HyperFlash to $DEST ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "$DEST\agents", "$DEST\skills\hyperflash\references", "$DEST\skills\hyperflash\scripts", "$DEST\rules", "$DEST\scripts" | Out-Null

Copy-Item "$PSScriptRoot\src\AGENTS.md" "$DEST\AGENTS.md" -Force
Copy-Item "$PSScriptRoot\src\rules\hyperflash-protocol.md" "$DEST\rules\" -Force
Copy-Item "$PSScriptRoot\src\agents\*.md" "$DEST\agents\" -Force
Copy-Item "$PSScriptRoot\src\skills\hyperflash\SKILL.md" "$DEST\skills\hyperflash\" -Force
Copy-Item "$PSScriptRoot\src\skills\hyperflash\references\*" "$DEST\skills\hyperflash\references\" -Force
Copy-Item "$PSScriptRoot\src\skills\hyperflash\scripts\*.py" "$DEST\skills\hyperflash\scripts\" -Force
Copy-Item "$PSScriptRoot\src\scripts\*.py" "$DEST\scripts\" -Force

# Non-destructive hook merge
$NormalizedDest = $DEST -replace '\\', '/'
$TemplateRaw = (Get-Content "$PSScriptRoot\src\hooks.json" -Raw) -replace '{{CONFIG_DIR}}', $NormalizedDest
$NewHooks = $TemplateRaw | ConvertFrom-Json

$DestHooksPath = Join-Path $DEST "hooks.json"
$ExistingHooks = @{}
if (Test-Path $DestHooksPath) {
    try {
        $ExistingHooks = (Get-Content $DestHooksPath -Raw | ConvertFrom-Json)
    } catch {}
}

foreach ($prop in $NewHooks.PSObject.Properties) {
    $ExistingHooks | Add-Member -MemberType NoteProperty -Name $prop.Name -Value $prop.Value -Force
}

$ExistingHooks | ConvertTo-Json -Depth 10 | Set-Content $DestHooksPath -Force

Write-Host "[OK] HyperFlash successfully installed!" -ForegroundColor Green
Write-Host "Type '@hyperflash' in the Antigravity Desktop IDE chat or run 'agy --agent hyperflash' in your terminal."
