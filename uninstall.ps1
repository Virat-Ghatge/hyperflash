$DEST = Join-Path $HOME ".gemini\config"
Write-Host "=== Uninstalling HyperFlash from $DEST ===" -ForegroundColor Yellow

Remove-Item "$DEST\agents\hyperflash*.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\skills\hyperflash" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\rules\hyperflash-protocol.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\build_symbol_graph.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\enforce_hyperflash_pre_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\mark_mutation_post_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\scripts\enforce_completion_stop_hook.py" -Force -ErrorAction SilentlyContinue

Write-Host "[OK] HyperFlash removed. Note: $DEST\hooks.json was retained to protect other tools." -ForegroundColor Green
