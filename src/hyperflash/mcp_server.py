"""
Model Context Protocol (MCP) stdio server for HyperFlash:
Exposes deterministic reliability tools to Cursor, Claude Code, Windsurf, and custom agent harnesses.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from hyperflash.core import (
    check_for_elision,
    generate_symbol_graph,
    load_contract,
    run_verification,
    save_contract,
)

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "hyperflash_safe_patch",
        "description": "Applies a surgical code patch to a file with Invariant 7 (Zero Elision) and Invariant 2 (Scope) guardrails.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "target_file": {
                    "type": "string",
                    "description": "Path to the target file relative to workspace root.",
                },
                "search_text": {
                    "type": "string",
                    "description": "Exact text substring to find and replace.",
                },
                "replacement_text": {
                    "type": "string",
                    "description": "100% complete replacement text without placeholder comments or truncations.",
                },
            },
            "required": ["target_file", "search_text", "replacement_text"],
        },
    },
    {
        "name": "hyperflash_verify",
        "description": "Executes the HyperFlash deterministic verification hierarchy (syntax, types, linter, tests).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "tier": {
                    "type": "integer",
                    "description": "Maximum verification tier to execute (1 to 9). Default is 6.",
                    "default": 6,
                },
                "custom_cmd": {
                    "type": "string",
                    "description": "Optional custom test or validation command to run.",
                    "default": "",
                },
            },
        },
    },
    {
        "name": "hyperflash_init_contract",
        "description": "Initializes or updates .agents/state/contract.json with operational mode, allowed write scope, and criteria.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "description": "Execution mode (implement, fix, refactor, direct).",
                    "default": "implement",
                },
                "allowed_scope": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of allowed file paths or directory prefixes for writes.",
                    "default": [],
                },
                "acceptance_criteria": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of explicit success criteria to satisfy.",
                    "default": [],
                },
            },
        },
    },
    {
        "name": "hyperflash_get_symbol_graph",
        "description": "Returns the workspace AST symbol graph detailing classes, methods, functions, and imports.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]


def hyperflash_safe_patch(
    target_file: str,
    search_text: str,
    replacement_text: str,
    workspace_dir: str = ".",
) -> str:
    """
    Applies surgical text replacement ensuring zero code elision and scope conformance.
    """
    # Invariant 7: Zero Elision
    has_elision, pattern = check_for_elision(replacement_text)
    if has_elision:
        return (
            f"ERROR: Invariant 7 Violation (Code Truncation Blocked): Prohibited elision pattern '{pattern}' detected. "
            "HyperFlash requires 100% complete, fully implemented code blocks."
        )

    workspace = Path(workspace_dir).resolve()
    target_path = (workspace / target_file).resolve()
    norm_target = str(target_path.as_posix())

    # Invariant 2: Scope Confinement
    contract_path = workspace / ".agents/state/contract.json"
    contract = load_contract(contract_path)
    allowed_scope = [str(Path(p).as_posix()) for p in contract.get("allowed_write_scope", [])]
    if allowed_scope:
        if not any(norm_target.endswith(s) or s in norm_target for s in allowed_scope):
            return (
                f"ERROR: Invariant 2 Violation (Out of Scope): '{target_file}' is outside allowed_write_scope {allowed_scope}."
            )

    if not target_path.exists():
        return f"ERROR: Target file '{target_file}' does not exist."

    try:
        content = target_path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"ERROR: Failed reading '{target_file}': {exc}"

    if search_text not in content:
        return f"ERROR: Search text not found in '{target_file}'."

    new_content = content.replace(search_text, replacement_text, 1)
    try:
        target_path.write_text(new_content, encoding="utf-8")
    except Exception as exc:
        return f"ERROR: Failed writing '{target_file}': {exc}"

    import time
    contract["last_mutation_ts"] = time.time()
    save_contract(contract, contract_path)
    return f"SUCCESS: Successfully patched '{target_file}'."


def hyperflash_verify(tier: int = 6, custom_cmd: str = "", workspace_dir: str = ".") -> str:
    """
    Runs deterministic verification hierarchy and returns formatted report.
    """
    result = run_verification(tier=tier, custom_cmd=custom_cmd, workspace_dir=workspace_dir)
    diagnostics_str = json.dumps(result.get("diagnostics", []), indent=2)
    return f"{result.get('verdict', 'VERDICT: UNKNOWN')}\n\nDiagnostics:\n{diagnostics_str}"


def hyperflash_init_contract(
    mode: str = "implement",
    allowed_scope: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    workspace_dir: str = ".",
) -> str:
    """
    Initializes contract state in active workspace.
    """
    workspace = Path(workspace_dir).resolve()
    contract_path = workspace / ".agents/state/contract.json"
    contract = load_contract(contract_path)
    contract["mode"] = mode
    contract["allowed_write_scope"] = allowed_scope or []
    contract["acceptance_criteria"] = acceptance_criteria or []
    contract["last_verdict"] = "PENDING"
    save_contract(contract, contract_path)
    return f"SUCCESS: Initialized contract at '{contract_path.as_posix()}' with mode='{mode}'."


def hyperflash_get_symbol_graph(workspace_dir: str = ".") -> str:
    """
    Generates and returns JSON AST symbol graph of active workspace.
    """
    graph = generate_symbol_graph(workspace_dir)
    return json.dumps(graph, indent=2)


def dispatch_tool_call(tool_name: str, arguments: dict[str, Any], workspace_dir: str = ".") -> tuple[str, bool]:
    """
    Routes tool calls to the appropriate implementation. Returns (output_text, is_error).
    """
    if tool_name == "hyperflash_safe_patch":
        target = str(arguments.get("target_file", ""))
        search = str(arguments.get("search_text", ""))
        repl = str(arguments.get("replacement_text", ""))
        res = hyperflash_safe_patch(target, search, repl, workspace_dir=workspace_dir)
        is_err = res.startswith("ERROR:")
        return res, is_err

    elif tool_name == "hyperflash_verify":
        tier_val = int(arguments.get("tier", 6))
        cmd_val = str(arguments.get("custom_cmd", ""))
        res = hyperflash_verify(tier=tier_val, custom_cmd=cmd_val, workspace_dir=workspace_dir)
        is_err = "FAIL" in res
        return res, is_err

    elif tool_name == "hyperflash_init_contract":
        mode_val = str(arguments.get("mode", "implement"))
        scope_val = arguments.get("allowed_scope", [])
        if not isinstance(scope_val, list):
            scope_val = []
        crit_val = arguments.get("acceptance_criteria", [])
        if not isinstance(crit_val, list):
            crit_val = []
        res = hyperflash_init_contract(
            mode=mode_val,
            allowed_scope=scope_val,
            acceptance_criteria=crit_val,
            workspace_dir=workspace_dir,
        )
        return res, False

    elif tool_name == "hyperflash_get_symbol_graph":
        res = hyperflash_get_symbol_graph(workspace_dir=workspace_dir)
        return res, False

    return f"ERROR: Unknown tool '{tool_name}'", True


def process_jsonrpc_request(req: dict[str, Any], workspace_dir: str = ".") -> dict[str, Any] | None:
    """
    Handles a single JSON-RPC 2.0 MCP request and returns the JSON-RPC response dict or None.
    """
    msg_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    # Notifications do not return a response
    if msg_id is None and method.startswith("notifications/"):
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "hyperflash",
                    "version": "1.0.0",
                },
            },
        }

    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {},
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": TOOL_DEFINITIONS,
            },
        }

    elif method == "tools/call":
        tool_name = str(params.get("name", ""))
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            arguments = {}
        output_text, is_error = dispatch_tool_call(tool_name, arguments, workspace_dir=workspace_dir)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": output_text,
                    }
                ],
                "isError": is_error,
            },
        }

    # Method not found
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": {
            "code": -32601,
            "message": f"Method '{method}' not found",
        },
    }


def run_stdio_server(workspace_dir: str = ".") -> None:
    """
    Main loop for MCP stdio server. Reads newline-delimited JSON-RPC from stdin.
    """
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {exc}",
                },
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
            continue

        resp = process_jsonrpc_request(req, workspace_dir=workspace_dir)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


def main() -> None:
    """CLI entrypoint for standalone MCP server."""
    run_stdio_server()


if __name__ == "__main__":
    main()
