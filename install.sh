#!/usr/bin/env bash
set -e

DEST="$HOME/.gemini/config"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing HyperFlash to $DEST ==="
mkdir -p "$DEST"/{agents,skills/hyperflash/references,skills/hyperflash/scripts,rules,scripts}

cp "$REPO_DIR/src/AGENTS.md" "$DEST/AGENTS.md"
cp "$REPO_DIR/src/rules/hyperflash-protocol.md" "$DEST/rules/"
cp "$REPO_DIR/src/agents/"*.md "$DEST/agents/"
cp "$REPO_DIR/src/skills/hyperflash/SKILL.md" "$DEST/skills/hyperflash/"
cp "$REPO_DIR/src/skills/hyperflash/references/"* "$DEST/skills/hyperflash/references/"
cp "$REPO_DIR/src/skills/hyperflash/scripts/"*.py "$DEST/skills/hyperflash/scripts/"
cp "$REPO_DIR/src/scripts/"*.py "$DEST/scripts/"

chmod +x "$DEST/scripts/"*.py "$DEST/skills/hyperflash/scripts/"*.py

# Non-destructive hooks.json merge via Python
python3 - << EOF
import json
from pathlib import Path

dest_hooks_path = Path("$DEST/hooks.json")
template_path = Path("$REPO_DIR/src/hooks.json")

template_raw = template_path.read_text(encoding="utf-8").replace("{{CONFIG_DIR}}", "$DEST")
new_hooks = json.loads(template_raw)

existing_hooks = {}
if dest_hooks_path.exists():
    try:
        existing_hooks = json.loads(dest_hooks_path.read_text(encoding="utf-8"))
    except Exception:
        existing_hooks = {}

# Merge hyperflash hooks without overwriting third-party hooks
for k, v in new_hooks.items():
    existing_hooks[k] = v

dest_hooks_path.write_text(json.dumps(existing_hooks, indent=2) + "\n", encoding="utf-8")
print("[HOOKS] Merged HyperFlash hooks into $DEST/hooks.json successfully.")
EOF

echo ""
echo "[OK] HyperFlash successfully installed!"
echo "Type '@hyperflash' in the Antigravity Desktop IDE chat or run 'agy --agent hyperflash' in your terminal."
