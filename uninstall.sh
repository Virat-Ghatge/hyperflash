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

# Prune only HyperFlash keys from hooks.json
python3 - << EOF
import json
from pathlib import Path

hooks_path = Path("$DEST/hooks.json")
if hooks_path.exists():
    try:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        pruned = {k: v for k, v in hooks.items() if not k.startswith("hyperflash-")}
        hooks_path.write_text(json.dumps(pruned, indent=2) + "\n", encoding="utf-8")
        print("[HOOKS] Pruned HyperFlash entries from hooks.json.")
    except Exception:
        pass
EOF

echo "[OK] HyperFlash uninstalled cleanly."
