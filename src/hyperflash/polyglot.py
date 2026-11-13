"""
Polyglot configuration generators for HyperFlash:
Enforces first-class native Agent Personas and guardrails for OpenCode, Claude Code, Cursor, Windsurf, Git Hooks, and Antigravity.
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

CURSOR_RULE_MDC_CONTENT: str = """---
description: HyperFlash Autonomous Engineering Reliability Agent
globs: *
alwaysApply: true
---
# HyperFlash Engineering Reliability Agent for Cursor

You are HYPERFLASH, the Principal Engineering Reliability Orchestrator.
1. GROUND BEFORE MUTATING: Always view the target file completely before proposing or executing edits.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Write 100% complete, fully implemented code blocks.
3. EXHAUSTIVE STATIC TYPING: Every function signature, parameter, and return type must carry explicit static type annotations.
4. STAY IN DECLARED SCOPE: Confine all changes strictly to files approved for the current task.
5. REPORT REALITY ONLY: Never claim tests passed or bugs are resolved unless verified by running compilation or test commands in this session.
6. BYTE-IDENTICAL LOOP REJECTION: Never retry an identical failed modification.
7. CHUNKED LONG-DECODE: For files over 200 lines, emit typed skeletons first, then populate method bodies in surgical diffs.
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

CLAUDE_COMMAND_MD_CONTENT: str = """---
description: Activate HyperFlash Autonomous Engineering Reliability Agent
---
You are now operating as HYPERFLASH, the Principal Engineering Reliability Orchestrator.
Strictly adhere to the HyperFlash 8 Invariants:
1. GROUND FIRST: Never call file editing tools without reading the target file completely first.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`.
3. CONTRACT BOUNDARY: Only mutate files explicitly discussed and approved for the current task.
4. EVIDENCE OVER CLAIMS: Never declare a task complete or a bug fixed unless verified with `hyperflash verify` in this session with exit code 0.
5. CHUNKED DECODE: For files over 200 lines, emit class/function skeletons first, then populate method bodies.
6. EXHAUSTIVE STATIC TYPING: Full static types on all functions, parameters, and returns.
7. NEVER EXACT-RETRY: Change your implementation strategy if an edit fails.
8. MCP TOOLS: Use HyperFlash MCP tools (`hyperflash_safe_patch`, `hyperflash_verify`) whenever available.
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

WINDSURF_RULE_MD_CONTENT: str = """---
description: HyperFlash Autonomous Engineering Reliability Agent
globs: *
alwaysApply: true
---
# HyperFlash Engineering Reliability Agent for Windsurf

You are HYPERFLASH, the Principal Engineering Reliability Orchestrator.
1. GROUND BEFORE MUTATING: Always view the target file completely before proposing or executing edits.
2. ZERO CODE ELISION: Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Write 100% complete, fully implemented code blocks.
3. EXHAUSTIVE STATIC TYPING: Every function signature, parameter, and return type must carry explicit static type annotations.
4. STAY IN DECLARED SCOPE: Confine all changes strictly to files approved for the current task.
5. REPORT REALITY ONLY: Never claim tests passed or bugs are resolved unless verified by running compilation or test commands in this session.
6. BYTE-IDENTICAL LOOP REJECTION: Never retry an identical failed modification.
7. CHUNKED LONG-DECODE: For files over 200 lines, emit typed skeletons first, then populate method bodies in surgical diffs.
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

OPENCODE_AGENT_DICT: dict[str, Any] = {
    "name": "HyperFlash",
    "description": "Universal Engineering Reliability & Multi-Agent Verification Runtime",
    "systemPrompt": (
        "You are HYPERFLASH, the Principal Multi-Agent Engineering Reliability Orchestrator. "
        "You operate strictly under the 8 HyperFlash Invariants: 1. Ground before mutating "
        "(read files completely before editing). 2. Stay in declared scope. 3. Fresh evidence "
        "required before completion. 4. Never exact-retry failed modifications. 5. Satisfy "
        "acceptance criteria. 6. Report reality only. 7. ZERO code elision (never write '// ... "
        "rest of code' or placeholder comments). 8. Exhaustive static typing on all functions. "
        "Always use hyperflash_safe_patch to mutate files, and run hyperflash_verify before claiming "
        "a task is done."
    ),
    "tools": [
        "hyperflash_safe_patch",
        "hyperflash_verify",
        "hyperflash_get_symbol_graph",
        "hyperflash_init_contract",
    ],
}

OPENCODE_CONFIG_DICT: dict[str, Any] = {
    "agent": "hyperflash",
    "agents": {
        "hyperflash": OPENCODE_AGENT_DICT,
    },
    "mcpServers": {
        "hyperflash": {
            "command": "hyperflash",
            "args": ["mcp"],
        }
    },
}

OPENCODE_GLOBAL_CONFIG_DICT: dict[str, Any] = {
    "agent": {
        "hyperflash": {
            "name": "HyperFlash",
            "description": "Universal Engineering Reliability & Multi-Agent Verification Runtime",
            "system": (
                "You are HYPERFLASH, the Principal Multi-Agent Engineering Reliability Orchestrator. "
                "You operate strictly under the 8 HyperFlash Invariants: 1. Ground before mutating. "
                "2. Stay in declared scope. 3. Fresh evidence required before completion. "
                "4. Never exact-retry failed modifications. 5. Satisfy acceptance criteria. "
                "6. Report reality only. 7. ZERO code elision. 8. Exhaustive static typing. "
                "Always use hyperflash_safe_patch to mutate files, and run hyperflash_verify before claiming a task is done."
            ),
        }
    },
    "mcp": {
        "servers": {
            "hyperflash": {
                "type": "local",
                "command": ["hyperflash", "mcp"],
            }
        }
    },
}

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
            "args": ["mcp"],
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
        if isinstance(mcp_servers, dict):
            mcp_servers.update(new_data["mcpServers"])
            existing["mcpServers"] = mcp_servers
        else:
            existing["mcpServers"] = new_data["mcpServers"]

    # Merge agents specifically if present
    if "agents" in new_data:
        agents = existing.get("agents", {})
        if isinstance(agents, dict):
            agents.update(new_data["agents"])
            existing["agents"] = agents
        else:
            existing["agents"] = new_data["agents"]

    # Merge nested 'agent' dict if both are dicts
    if "agent" in new_data:
        if isinstance(new_data["agent"], dict):
            agent_dict = existing.get("agent", {})
            if isinstance(agent_dict, dict):
                agent_dict.update(new_data["agent"])
                existing["agent"] = agent_dict
            else:
                existing["agent"] = new_data["agent"]
        else:
            existing["agent"] = new_data["agent"]

    # Merge nested 'mcp' dict (OpenCode global config schema: {"mcp": {"servers": {...}}})
    if "mcp" in new_data:
        if isinstance(new_data["mcp"], dict):
            mcp_dict = existing.get("mcp", {})
            if isinstance(mcp_dict, dict):
                servers = mcp_dict.get("servers", {})
                new_servers = new_data["mcp"].get("servers", {})
                if isinstance(servers, dict) and isinstance(new_servers, dict):
                    servers.update(new_servers)
                    mcp_dict["servers"] = servers
                else:
                    mcp_dict.update(new_data["mcp"])
                existing["mcp"] = mcp_dict
            else:
                existing["mcp"] = new_data["mcp"]
        else:
            existing["mcp"] = new_data["mcp"]

    for k, v in new_data.items():
        if k not in ("mcpServers", "agents", "agent", "mcp"):
            existing[k] = v

    file_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def setup_cursor(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Configures HyperFlash rules, agent rule mdc, and stdio MCP server for Cursor.
    """
    target_root = Path.home() if is_global else Path(workspace_dir).resolve()
    created_files: list[str] = []

    rules_path = target_root / ".cursorrules"
    rules_path.write_text(CURSOR_RULES_CONTENT, encoding="utf-8")
    created_files.append(str(rules_path))

    rules_dir = target_root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    mdc_path = rules_dir / "hyperflash.mdc"
    mdc_path.write_text(CURSOR_RULE_MDC_CONTENT, encoding="utf-8")
    created_files.append(str(mdc_path))

    mcp_path = target_root / ".cursor" / "mcp.json"
    merge_json_config(mcp_path, MCP_CONFIG_DICT)
    created_files.append(str(mcp_path))

    return created_files


def setup_claude(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Configures HyperFlash rules, slash command, and stdio MCP server for Claude Code.
    """
    created_files: list[str] = []

    if is_global:
        home = Path.home()
        commands_dir = home / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        cmd_file = commands_dir / "hyperflash.md"
        cmd_file.write_text(CLAUDE_COMMAND_MD_CONTENT, encoding="utf-8")
        created_files.append(str(cmd_file))

        claude_json = home / ".claude.json"
        merge_json_config(claude_json, MCP_CONFIG_DICT)
        created_files.append(str(claude_json))
    else:
        workspace = Path(workspace_dir).resolve()

        claude_md = workspace / "CLAUDE.md"
        claude_md.write_text(CLAUDE_MD_CONTENT, encoding="utf-8")
        created_files.append(str(claude_md))

        commands_dir = workspace / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)
        cmd_file = commands_dir / "hyperflash.md"
        cmd_file.write_text(CLAUDE_COMMAND_MD_CONTENT, encoding="utf-8")
        created_files.append(str(cmd_file))

        claude_json = workspace / ".claude.json"
        merge_json_config(claude_json, MCP_CONFIG_DICT)
        created_files.append(str(claude_json))

    return created_files


def setup_windsurf(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Configures HyperFlash rules, agent persona rule, and stdio MCP server for Windsurf.
    """
    target_root = Path.home() if is_global else Path(workspace_dir).resolve()
    created_files: list[str] = []

    rules_path = target_root / ".windsurfrules"
    rules_path.write_text(WINDSURF_RULES_CONTENT, encoding="utf-8")
    created_files.append(str(rules_path))

    rules_dir = target_root / ".windsurf" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    rule_md_path = rules_dir / "hyperflash.md"
    rule_md_path.write_text(WINDSURF_RULE_MD_CONTENT, encoding="utf-8")
    created_files.append(str(rule_md_path))

    mcp_path = target_root / ".windsurf" / "mcp.json"
    merge_json_config(mcp_path, MCP_CONFIG_DICT)
    created_files.append(str(mcp_path))

    return created_files


def setup_git_hooks(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Installs HyperFlash pre-commit hook into .git/hooks.
    """
    workspace = Path(workspace_dir).resolve()
    git_hooks_dir = workspace / ".git" / "hooks"
    created_files: list[str] = []

    if is_global and not (workspace / ".git").exists():
        return created_files

    git_hooks_dir.mkdir(parents=True, exist_ok=True)

    hook_file = git_hooks_dir / "pre-commit"
    hook_file.write_text(GIT_PRE_COMMIT_CONTENT, encoding="utf-8")

    # Set executable permissions on POSIX
    if os.name != "nt":
        current_stat = hook_file.stat()
        hook_file.chmod(current_stat.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    created_files.append(str(hook_file))
    return created_files


def setup_antigravity(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Installs or updates HyperFlash skill and agents in Antigravity (~/.gemini/config/).
    """
    home = Path.home()
    config_dir = home / ".gemini" / "config"
    created_files: list[str] = []

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


def setup_opencode(workspace_dir: Path | str = ".", is_global: bool = False) -> list[str]:
    """
    Configures HyperFlash rules, agent persona, and stdio MCP server for OpenCode.
    If is_global is True, writes to user global config: ~/.config/opencode/opencode.json.
    If not purely global, also writes local workspace files: OPENCODE.md, .opencode/agents/hyperflash.json, opencode.json.
    """
    created_files: list[str] = []

    if is_global:
        global_config_path = Path.home() / ".config" / "opencode" / "opencode.json"
        merge_json_config(global_config_path, OPENCODE_GLOBAL_CONFIG_DICT)
        created_files.append(str(global_config_path))
    else:
        workspace = Path(workspace_dir).resolve()

        opencode_md = workspace / "OPENCODE.md"
        opencode_md.write_text(OPENCODE_MD_CONTENT, encoding="utf-8")
        created_files.append(str(opencode_md))

        agent_dir = workspace / ".opencode" / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent_json_path = agent_dir / "hyperflash.json"
        agent_json_path.write_text(json.dumps(OPENCODE_AGENT_DICT, indent=2), encoding="utf-8")
        created_files.append(str(agent_json_path))

        opencode_json = workspace / "opencode.json"
        merge_json_config(opencode_json, OPENCODE_CONFIG_DICT)
        created_files.append(str(opencode_json))

    return created_files


def setup_all(workspace_dir: Path | str = ".", is_global: bool = False) -> dict[str, list[str]]:
    """
    Executes polyglot configuration across all supported platforms.
    """
    return {
        "cursor": setup_cursor(workspace_dir, is_global=is_global),
        "claude": setup_claude(workspace_dir, is_global=is_global),
        "windsurf": setup_windsurf(workspace_dir, is_global=is_global),
        "git": setup_git_hooks(workspace_dir, is_global=is_global),
        "antigravity": setup_antigravity(workspace_dir, is_global=is_global),
        "opencode": setup_opencode(workspace_dir, is_global=is_global),
    }
