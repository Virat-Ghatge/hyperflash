"""
Unit tests for hyperflash.mcp_server:
Tests MCP tool execution, Invariant 7 interception, and JSON-RPC 2.0 protocol handling.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hyperflash.mcp_server import (
    hyperflash_get_symbol_graph,
    hyperflash_init_contract,
    hyperflash_safe_patch,
    hyperflash_verify,
    process_jsonrpc_request,
)


def test_mcp_safe_patch_rejects_elision(tmp_path: Path) -> None:
    """Verifies that hyperflash_safe_patch blocks edits containing elision comments."""
    target_file = tmp_path / "service.py"
    target_file.write_text("def process():\n    return 'old'\n", encoding="utf-8")

    res = hyperflash_safe_patch(
        target_file="service.py",
        search_text="return 'old'",
        replacement_text="// ... rest of implementation",
        workspace_dir=str(tmp_path),
    )
    assert res.startswith("ERROR: Invariant 7 Violation")
    # File content remains unchanged
    assert "return 'old'" in target_file.read_text(encoding="utf-8")


def test_mcp_safe_patch_enforces_scope(tmp_path: Path) -> None:
    """Verifies that hyperflash_safe_patch blocks edits outside declared contract scope."""
    # Initialize contract with scope restricted to "allowed.py"
    hyperflash_init_contract(
        mode="implement",
        allowed_scope=["allowed.py"],
        workspace_dir=str(tmp_path),
    )

    unauthorized_file = tmp_path / "secret.py"
    unauthorized_file.write_text("API_KEY = 'old'\n", encoding="utf-8")

    res = hyperflash_safe_patch(
        target_file="secret.py",
        search_text="API_KEY = 'old'",
        replacement_text="API_KEY = 'new'",
        workspace_dir=str(tmp_path),
    )
    assert res.startswith("ERROR: Invariant 2 Violation")
    assert "API_KEY = 'old'" in unauthorized_file.read_text(encoding="utf-8")


def test_mcp_safe_patch_success(tmp_path: Path) -> None:
    """Verifies successful patch application within scope."""
    hyperflash_init_contract(
        mode="implement",
        allowed_scope=["valid.py"],
        workspace_dir=str(tmp_path),
    )

    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def greet():\n    return 'hello'\n", encoding="utf-8")

    res = hyperflash_safe_patch(
        target_file="valid.py",
        search_text="return 'hello'",
        replacement_text="return 'world'",
        workspace_dir=str(tmp_path),
    )
    assert res.startswith("SUCCESS:")
    assert "return 'world'" in valid_file.read_text(encoding="utf-8")


def test_mcp_get_symbol_graph(tmp_path: Path) -> None:
    """Verifies symbol graph tool returns valid JSON matching workspace files."""
    code_file = tmp_path / "example.py"
    code_file.write_text("def calculate(x: int) -> int:\n    return x * 2\n", encoding="utf-8")

    graph_str = hyperflash_get_symbol_graph(workspace_dir=str(tmp_path))
    graph = json.loads(graph_str)
    assert "example.py" in graph
    assert "functions" in graph["example.py"]


def test_mcp_verify_tool(tmp_path: Path) -> None:
    """Verifies verification tool output."""
    (tmp_path / "clean.py").write_text("X = 1\n", encoding="utf-8")
    report = hyperflash_verify(tier=1, workspace_dir=str(tmp_path))
    assert "VERDICT: PASS" in report


def test_jsonrpc_protocol_flow(tmp_path: Path) -> None:
    """Verifies JSON-RPC 2.0 lifecycle: initialize, ping, tools/list, tools/call."""
    # 1. Initialize
    init_req: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {"protocolVersion": "2024-11-05"},
    }
    init_resp = process_jsonrpc_request(init_req, workspace_dir=str(tmp_path))
    assert init_resp is not None
    assert init_resp["id"] == 1
    assert init_resp["result"]["serverInfo"]["name"] == "hyperflash"

    # 2. Ping
    ping_req: dict[str, Any] = {"jsonrpc": "2.0", "id": 2, "method": "ping"}
    ping_resp = process_jsonrpc_request(ping_req, workspace_dir=str(tmp_path))
    assert ping_resp is not None
    assert ping_resp["result"] == {}

    # 3. Notification (no response)
    notif_req: dict[str, Any] = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    notif_resp = process_jsonrpc_request(notif_req, workspace_dir=str(tmp_path))
    assert notif_resp is None

    # 4. Tools List
    list_req: dict[str, Any] = {"jsonrpc": "2.0", "id": 3, "method": "tools/list"}
    list_resp = process_jsonrpc_request(list_req, workspace_dir=str(tmp_path))
    assert list_resp is not None
    tool_names = [t["name"] for t in list_resp["result"]["tools"]]
    assert "hyperflash_safe_patch" in tool_names
    assert "hyperflash_verify" in tool_names
    assert "hyperflash_init_contract" in tool_names
    assert "hyperflash_get_symbol_graph" in tool_names

    # 5. Tool Call: safe_patch with elision rejection
    (tmp_path / "code.py").write_text("x = 1\n", encoding="utf-8")
    call_req: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "hyperflash_safe_patch",
            "arguments": {
                "target_file": "code.py",
                "search_text": "x = 1",
                "replacement_text": "# ... rest of code",
            },
        },
    }
    call_resp = process_jsonrpc_request(call_req, workspace_dir=str(tmp_path))
    assert call_resp is not None
    assert call_resp["result"]["isError"] is True
    assert "Invariant 7 Violation" in call_resp["result"]["content"][0]["text"]
