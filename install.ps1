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

# Interpolate {{CONFIG_DIR}} for hooks.json
$HooksTemplate = Get-Content "$PSScriptRoot\src\hooks.json" -Raw
$NormalizedDest = $DEST -replace '\\', '/'
$HooksFinal = $HooksTemplate -replace '\{\{CONFIG_DIR\}\}', $NormalizedDest
Set-Content "$DEST\hooks.json" $HooksFinal -Force

Write-Host "[OK] HyperFlash successfully installed!" -ForegroundColor Green
Write-Host "Type '@hyperflash' in the Antigravity IDE chat or run 'agy --agent hyperflash' in your terminal."
