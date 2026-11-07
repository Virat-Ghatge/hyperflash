$DEST = Join-Path $HOME ".gemini\config"
Write-Host "=== Uninstalling HyperFlash from $DEST ===" -ForegroundColor Yellow

Remove-Item "$DEST\agents\hyperflash*.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\skills\hyperflash" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\rules\hyperflash-protocol.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\build_symbol_graph.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\enforce_hyperflash_pre_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\mark_mutation_post_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\enforce_completion_stop_hook.py" -Force -ErrorAction SilentlyContinue

# Prune only HyperFlash keys from hooks.json
$DestHooksPath = Join-Path $DEST "hooks.json"
if (Test-Path $DestHooksPath) {
    try {
        $ExistingHooks = Get-Content $DestHooksPath -Raw | ConvertFrom-Json
        $PrunedHooks = [ordered]@{}
        foreach ($prop in $ExistingHooks.PSObject.Properties) {
            if (-not $prop.Name.StartsWith("hyperflash-")) {
                $PrunedHooks[$prop.Name] = $prop.Value
            }
        }
        $PrunedHooks | ConvertTo-Json -Depth 10 | Set-Content $DestHooksPath -Force
        Write-Host "[HOOKS] Pruned HyperFlash entries from $DestHooksPath." -ForegroundColor Cyan
    } catch {}
}

Write-Host "[OK] HyperFlash uninstalled cleanly." -ForegroundColor Green
