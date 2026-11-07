#!/usr/bin/env bash
set -e

DEST="$HOME/.gemini/config"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing HyperFlash to $DEST ==="
mkdir -p "$DEST"/{agents,skills/hyperflash/references,skills/hyperflash/scripts,rules,scripts}

cp "$REPO_DIR/src/AGENTS.md" "$DEST/AGENTS.md"
cp "$REPO_DIR/src/hooks.json" "$DEST/hooks.json"
cp "$REPO_DIR/src/rules/hyperflash-protocol.md" "$DEST/rules/"
cp "$REPO_DIR/src/agents/"*.md "$DEST/agents/"
cp "$REPO_DIR/src/skills/hyperflash/SKILL.md" "$DEST/skills/hyperflash/"
cp "$REPO_DIR/src/skills/hyperflash/references/"* "$DEST/skills/hyperflash/references/"
cp "$REPO_DIR/src/skills/hyperflash/scripts/"*.py "$DEST/skills/hyperflash/scripts/"
cp "$REPO_DIR/src/scripts/"*.py "$DEST/scripts/"

# Adjust hooks.json paths to match local installation directory
sed -i "s|C:/Users/[^/]*/\.gemini/config|$DEST|g" "$DEST/hooks.json" 2>/dev/null || sed -i '' "s|C:/Users/[^/]*/\.gemini/config|$DEST|g" "$DEST/hooks.json" 2>/dev/null || true

chmod +x "$DEST/scripts/"*.py "$DEST/skills/hyperflash/scripts/"*.py

echo "[OK] HyperFlash successfully installed!"
echo "Run 'agy --agent hyperflash' or mention '@hyperflash' in the Antigravity IDE."
