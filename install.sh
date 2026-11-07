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

# Interpolate {{CONFIG_DIR}} into destination hooks.json
sed "s|{{CONFIG_DIR}}|$DEST|g" "$REPO_DIR/src/hooks.json" > "$DEST/hooks.json"

chmod +x "$DEST/scripts/"*.py "$DEST/skills/hyperflash/scripts/"*.py

echo "[OK] HyperFlash successfully installed!"
echo "Type '@hyperflash' in the Antigravity IDE chat or run 'agy --agent hyperflash' in your terminal."
