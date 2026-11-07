$DEST = Join-Path $HOME ".gemini\config"
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "=== Installing HyperFlash to $DEST ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "$DEST\\agents", "$DEST\\skills\\hyperflash\\references", "$DEST\\skills\\hyperflash\\scripts", "$DEST\\rules", "$DEST\\scripts" | Out-Null

Copy-Item "$PSScriptRoot\\src\\AGENTS.md" "$DEST\\AGENTS.md" -Force
Copy-Item "$PSScriptRoot\\src\\hooks.json" "$DEST\\hooks.json" -Force
Copy-Item "$PSScriptRoot\\src\\rules\\hyperflash-protocol.md" "$DEST\\rules\\" -Force
Copy-Item "$PSScriptRoot\\src\\agents\\*.md" "$DEST\\agents\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\SKILL.md" "$DEST\\skills\\hyperflash\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\references\\*" "$DEST\\skills\\hyperflash\\references\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\scripts\\*.py" "$DEST\\skills\\hyperflash\\scripts\\" -Force
Copy-Item "$PSScriptRoot\\src\\scripts\\*.py" "$DEST\\scripts\\" -Force

# Normalize hook paths in hooks.json
$destNormalized = $DEST -replace '\\\\', '/'
$hooksFile = "$DEST\\hooks.json"
if (Test-Path $hooksFile) {
    $content = Get-Content $hooksFile -Raw
    $content = $content -replace 'C:/Users/[^/]+/\.gemini/config', $destNormalized
    Set-Content $hooksFile -Value $content -NoNewline
}

Write-Host "[OK] HyperFlash successfully installed!" -ForegroundColor Green
Write-Host "Run 'agy --agent hyperflash' or mention '@hyperflash' in the Antigravity IDE."
