#!/usr/bin/env bash
set -e

DEST="$HOME/.gemini/config"
echo "=== Uninstalling HyperFlash from $DEST ==="

rm -f "$DEST/agents/hyperflash"*.md
rm -rf "$DEST/skills/hyperflash"
rm -f "$DEST/rules/hyperflash-protocol.md"
rm -f "$DEST/scripts/build_symbol_graph.py"
rm -f "$DEST/scripts/enforce_hyperflash_pre_hook.py"
rm -f "$DEST/scripts/mark_mutation_post_hook.py"
rm -f "$DEST/scripts/enforce_completion_stop_hook.py"

echo "[OK] HyperFlash removed. Note: $DEST/hooks.json was retained to protect other tools."
