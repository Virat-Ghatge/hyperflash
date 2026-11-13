"""
Polyglot configuration generators for HyperFlash:
Enables 1-click instant setup for Cursor, Claude Code, Windsurf, Git Hooks, Antigravity, and OpenCode.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
from pathlib import Path
from typing import Any

CURSOR_RULES_CONTENT: str = """# HyperFlash Engineering Rules for Cursor

1. GROUND BEFORE MUTATING: Always view the target file completely before proposing or executing edits.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Write 100% complete, fully implemented code blocks.
3. EXHAUSTIVE STATIC TYPING: Every function signature, parameter, and return type must carry explicit static type annotations.
4. STAY IN DECLARED SCOPE: Confine all changes strictly to files approved for the current task. Do not drift into unrelated modules.
5. REPORT REALITY ONLY: Never claim tests passed or bugs are resolved unless verified by running compilation or test commands in this session.
6. BYTE-IDENTICAL LOOP REJECTION: Never retry an identical failed modification. Alter implementation strategy if a patch fails.
7. CHUNKED LONG-DECODE: For files over 200 lines, emit typed class/function skeletons first, then populate method bodies in surgical diffs.
8. MANDATORY VERIFICATION: Always run project verification (`pytest`, `tsc`, `npm test`, or `hyperflash verify`) before concluding tasks.
"""

CLAUDE_MD_CONTENT: str = """# HyperFlash Reliability Constitution for Claude Code

1. GROUND FIRST: Never call file editing tools on an existing file without calling View or Cat first in this session.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Every edit must be 100% complete and executable.
3. CONTRACT BOUNDARY: Only mutate files explicitly discussed and approved for the current task. Do not touch external modules.
4. EVIDENCE OVER CLAIMS: Never declare a task complete or a bug fixed unless you have executed the project test command in this session and observed exit code 0.
5. CHUNKED DECODE: For files exceeding 200 lines, emit class/function skeletons first, then populate method bodies in surgical 100-150 line diffs.
6. EXHAUSTIVE STATIC TYPING: Full static types on all functions, parameters, and returns.
7. NEVER EXACT-RETRY: Change your approach if an edit or test fails.
8. AUTOMATED VERIFICATION: Run `hyperflash verify` to validate syntax, typing, linting, and tests.
"""

WINDSURF_RULES_CONTENT: str = """# HyperFlash Engineering Rules for Windsurf

1. GROUND BEFORE MUTATING: Always view the target file completely before proposing or executing edits.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Write 100% complete, fully implemented code blocks.
3. EXHAUSTIVE STATIC TYPING: Every function signature, parameter, and return type must carry explicit static type annotations.
4. STAY IN DECLARED SCOPE: Confine all changes strictly to files approved for the current task. Do not drift into unrelated modules.
5. REPORT REALITY ONLY: Never claim tests passed or bugs are resolved unless verified by running compilation or test commands in this session.
6. BYTE-IDENTICAL LOOP REJECTION: Never retry an identical failed modification. Alter implementation strategy if a patch fails.
7. CHUNKED LONG-DECODE: For files over 200 lines, emit typed class/function skeletons first, then populate method bodies in surgical diffs.
8. MANDATORY VERIFICATION: Always run project verification (`pytest`, `tsc`, `npm test`, or `hyperflash verify`) before concluding tasks.
"""

OPENCODE_MD_CONTENT: str = """# HyperFlash Reliability Constitution for OpenCode

1. GROUND BEFORE MUTATING: Always view the target file completely before executing edits.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Every edit must be 100% complete and functional.
3. EXHAUSTIVE STATIC TYPING: Every function signature, parameter, and return type must carry explicit static type annotations.
4. CONTRACT BOUNDARY: Only mutate files explicitly declared in the task scope.
5. EVIDENCE OVER CLAIMS: Never declare a task complete or a bug fixed unless verified with `hyperflash verify` in this session.
6. CHUNKED LONG-DECODE: For files exceeding 200 lines, emit typed class/function skeletons first, then populate method bodies in surgical diffs.
7. NEVER EXACT-RETRY: Change your implementation strategy if an edit or test fails.
8. DETERMINISTIC MCP TOOLS: Prefer using HyperFlash MCP tools (`hyperflash_safe_patch`, `hyperflash_verify`, `hyperflash_get_symbol_graph`) to prevent elision and verify changes.
"""

GIT_PRE_COMMIT_CONTENT: str = """#!/usr/bin/env bash
# HyperFlash Zero-Elision & Integrity Gate
set -e
echo "⚡ Running HyperFlash pre-commit audit..."

# Check for lazy elision patterns in staged changes
if git diff --cached | grep -E '(//|#|/\\*)[[:space:]]*(\\.\\.\\.|rest of|existing code|TODO: implement)'; then
    echo "❌ [HYPERFLASH ERROR] Code elision detected in staged changes!"
    echo "   Never commit '// ... rest of code' or placeholder comments."
    exit 1
fi

# Optional verification if hyperflash is in PATH
if command -v hyperflash &> /dev/null; then
    hyperflash verify --tier 5 || {
        echo "❌ [HYPERFLASH ERROR] Verification hierarchy failed."
        exit 1
    }
fi

echo "✅ HyperFlash checks passed."
exit 0
"""

MCP_CONFIG_DICT: dict[str, Any] = {
    "mcpServers": {
        "hyperflash": {
            "command": "hyperflash",
            "args": ["mcp"]
        }
    }
}


def merge_json_config(file_path: Path, new_data: dict[str, Any]) -> None:
    """
    Safely merges new_data into an existing JSON file without deleting existing keys.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, Any] = {}
    if file_path.is_file():
        try:
            existing = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    # Merge mcpServers specifically if present
    if "mcpServers" in new_data:
        mcp_servers = existing.get("mcpServers", {})
        mcp_servers.update(new_data["mcpServers"])
        existing["mcpServers"] = mcp_servers

    for k, v in new_data.items():
        if k != "mcpServers":
            existing[k] = v

    file_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def setup_cursor(workspace_dir: Path | str = ".") -> list[str]:
    """
    Configures HyperFlash rules and stdio MCP server for Cursor.
    """
    workspace = Path(workspace_dir).resolve()
    created_files: list[str] = []

    rules_path = workspace / ".cursorrules"
    rules_path.write_text(CURSOR_RULES_CONTENT, encoding="utf-8")
    created_files.append(str(rules_path))

    mcp_path = workspace / ".cursor" / "mcp.json"
    merge_json_config(mcp_path, MCP_CONFIG_DICT)
    created_files.append(str(mcp_path))

    return created_files


def setup_claude(workspace_dir: Path | str = ".") -> list[str]:
    """
    Configures HyperFlash rules and stdio MCP server for Claude Code.
    """
    workspace = Path(workspace_dir).resolve()
    created_files: list[str] = []

    claude_md = workspace / "CLAUDE.md"
    claude_md.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
    created_files.append(str(claude_md))

    claude_json = workspace / ".claude.json"
    merge_json_config(claude_json, MCP_CONFIG_DICT)
    created_files.append(str(claude_json))

    return created_files


def setup_windsurf(workspace_dir: Path | str = ".") -> list[str]:
    """
    Configures HyperFlash rules and stdio MCP server for Windsurf.
    """
    workspace = Path(workspace_dir).resolve()
    created_files: list[str] = []

    rules_path = workspace / ".windsurfrules"
    rules_path.write_text(WINDSURF_RULES_CONTENT, encoding="utf-8")
    created_files.append(str(rules_path))

    mcp_path = workspace / ".windsurf" / "mcp.json"
    merge_json_config(mcp_path, MCP_CONFIG_DICT)
    created_files.append(str(mcp_path))

    return created_files


def setup_git_hooks(workspace_dir: Path | str = ".") -> list[str]:
    """
    Installs HyperFlash pre-commit hook into .git/hooks.
    """
    workspace = Path(workspace_dir).resolve()
    git_hooks_dir = workspace / ".git" / "hooks"
    created_files: list[str] = []

    if not (workspace / ".git").exists():
        # Not a git root, create directory anyway for user convenience
        git_hooks_dir.mkdir(parents=True, exist_ok=True)
    else:
        git_hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_file = git_hooks_dir / "pre-commit"
    hook_file.write_text(GIT_PRE_COMMIT_CONTENT, encoding="utf-8")

    # Set executable permissions on POSIX
    if os.name != "nt":
        current_stat = hook_file.stat()
        hook_file.chmod(current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    created_files.append(str(hook_file))
    return created_files


def setup_antigravity(workspace_dir: Path | str = ".") -> list[str]:
    """
    Installs or updates HyperFlash skill and agents in Antigravity (~/.gemini/config/).
    """
    home = Path.home()
    config_dir = home / ".gemini" / "config"
    created_files: list[str] = []

    # If local repo has src/skills/hyperflash, copy to target
    repo_root = Path(workspace_dir).resolve()
    local_skill = repo_root / "src" / "skills" / "hyperflash"
    dest_skill = config_dir / "skills" / "hyperflash"

    if local_skill.exists():
        dest_skill.parent.mkdir(parents=True, exist_ok=True)
        if dest_skill.exists():
            shutil.rmtree(dest_skill)
        shutil.copytree(local_skill, dest_skill)
        created_files.append(str(dest_skill))

    local_agents = repo_root / "src" / "agents"
    dest_agents = config_dir / "agents"
    if local_agents.exists():
        dest_agents.mkdir(parents=True, exist_ok=True)
        for agent_file in local_agents.glob("*.md"):
            dest_file = dest_agents / agent_file.name
            shutil.copy2(agent_file, dest_file)
            created_files.append(str(dest_file))

    local_rules = repo_root / "src" / "rules"
    dest_rules = config_dir / "rules"
    if local_rules.exists():
        dest_rules.mkdir(parents=True, exist_ok=True)
        for rule_file in local_rules.glob("*.md"):
            dest_file = dest_rules / rule_file.name
            shutil.copy2(rule_file, dest_file)
            created_files.append(str(dest_file))

    return created_files


def setup_opencode(workspace_dir: Path | str = ".") -> list[str]:
    """
    Configures HyperFlash rules and stdio MCP server for OpenCode.
    """
    workspace = Path(workspace_dir).resolve()
    created_files: list[str] = []

    opencode_md = workspace / "OPENCODE.md"
    opencode_md.write_text(OPENCODE_MD_CONTENT, encoding="utf-8")
    created_files.append(str(opencode_md))

    opencode_json = workspace / "opencode.json"
    merge_json_config(opencode_json, MCP_CONFIG_DICT)
    created_files.append(str(opencode_json))

    return created_files


def setup_all(workspace_dir: Path | str = ".") -> dict[str, list[str]]:
    """
    Executes polyglot configuration across all supported platforms.
    """
    return {
        "cursor": setup_cursor(workspace_dir),
        "claude": setup_claude(workspace_dir),
        "windsurf": setup_windsurf(workspace_dir),
        "git": setup_git_hooks(workspace_dir),
        "antigravity": setup_antigravity(workspace_dir),
        "opencode": setup_opencode(workspace_dir),
    }
