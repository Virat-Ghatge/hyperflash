"""
Unit tests for hyperflash.core module:
Tests elision detection, symbol graph generation, contract lifecycle, and verification runner.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from hyperflash.core import (
    HyperFlashRuntime,
    check_for_elision,
    enforce_elision_guard,
    generate_symbol_graph,
    index_python_source,
    load_contract,
    run_verification,
    save_contract,
)
from hyperflash.polyglot import (
    GIT_PRE_COMMIT_CONTENT,
    setup_claude,
    setup_cline,
    setup_git_hook,
    setup_opencode,
    setup_roo,
    setup_windsurf,
)


def test_check_for_elision_detects_prohibited_patterns() -> None:
    """Verifies that all lazy truncation patterns are accurately detected."""
    prohibited_samples: list[str] = [
        "def calculate_total():\n    // ... rest of code",
        "# ... existing code remains unchanged",
        "class Service:\n    /* ... helper methods ... */",
        "def fetch_data():\n    # TODO: implement authentication",
        "// ...\n",
        "# ...\n",
        "/* existing code */",
        "<!-- ... -->",
    ]

    for sample in prohibited_samples:
        has_elision, pattern = check_for_elision(sample)
        assert has_elision is True, f"Failed to detect elision in sample: {sample}"
        assert len(pattern) > 0


def test_check_for_elision_permits_clean_code() -> None:
    """Verifies that clean production code with standard comments passes without false positives."""
    clean_samples: list[str] = [
        "def add(a: int, b: int) -> int:\n    return a + b",
        "# This calculates the total revenue based on Q3 projections\ndef calculate():\n    return 42",
        "// Standard inline comment explaining why we add 1\nconst x = y + 1;",
        "/* Multi-line comment\n   documenting an architecture decision */",
    ]

    for sample in clean_samples:
        has_elision, pattern = check_for_elision(sample)
        assert has_elision is False, f"False positive detected on sample: {sample} (matched: {pattern})"
        assert pattern == ""


def test_enforce_elision_guard_raises_on_truncation() -> None:
    """Verifies that enforce_elision_guard raises ValueError on elided code."""
    with pytest.raises(ValueError) as exc_info:
        enforce_elision_guard("def test():\n    # ... existing code")
    assert "Invariant 7 Violation" in str(exc_info.value)

    # Should not raise on clean code
    enforce_elision_guard("def test():\n    return True")


def test_index_python_source_extracts_symbols() -> None:
    """Verifies AST extraction of classes, methods, functions, and imports."""
    sample_code: str = (
        "import os\n"
        "from pathlib import Path\n\n"
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "async def fetch_async(url: str) -> str:\n"
        "    return url\n\n"
        "class Calculator:\n"
        "    def multiply(self, x: float, y: float) -> float:\n"
        "        return x * y\n"
    )

    symbols = index_python_source(sample_code, "sample.py")
    assert "imports" in symbols
    assert len(symbols["imports"]) == 2
    assert "functions" in symbols
    assert len(symbols["functions"]) == 2
    assert any("add" in f and "int" in f for f in symbols["functions"])
    assert any("async def fetch_async" in f for f in symbols["functions"])
    assert "classes" in symbols
    assert any("Calculator" in k for k in symbols["classes"].keys())


def test_generate_symbol_graph_on_workspace(tmp_path: Path) -> None:
    """Verifies indexing across directories in a workspace."""
    module_dir = tmp_path / "pkg"
    module_dir.mkdir()
    (module_dir / "math_ops.py").write_text(
        "def subtract(a: int, b: int) -> int:\n    return a - b\n",
        encoding="utf-8",
    )

    graph = generate_symbol_graph(tmp_path)
    assert len(graph) == 1
    rel_key = "pkg/math_ops.py"
    assert rel_key in graph
    assert "functions" in graph[rel_key]
    assert any("subtract" in fn for fn in graph[rel_key]["functions"])


def test_load_and_save_contract(tmp_path: Path) -> None:
    """Verifies contract loading, modification, and saving."""
    contract_file = tmp_path / ".agents" / "state" / "contract.json"
    default_contract = load_contract(contract_file)
    assert default_contract["mode"] == "implement"
    assert default_contract["allowed_write_scope"] == []

    default_contract["mode"] = "refactor"
    default_contract["allowed_write_scope"] = ["src/module.py"]
    save_contract(default_contract, contract_file)

    reloaded = load_contract(contract_file)
    assert reloaded["mode"] == "refactor"
    assert reloaded["allowed_write_scope"] == ["src/module.py"]


def test_runtime_safe_patch_and_scope(tmp_path: Path) -> None:
    """Verifies HyperFlashRuntime safe_patch enforcement of scope and elision."""
    runtime = HyperFlashRuntime(workspace_dir=tmp_path)
    target_file = tmp_path / "app.py"
    target_file.write_text("def hello():\n    return 'old'\n", encoding="utf-8")

    # Set contract scope allowing app.py
    runtime.init_contract(mode="implement", allowed_scope=["app.py"])

    # Patch with prohibited elision should fail
    with pytest.raises(ValueError):
        runtime.safe_patch("app.py", "return 'old'", "# ... rest of implementation")

    # Patch outside scope should fail
    runtime.init_contract(mode="implement", allowed_scope=["other.py"])
    with pytest.raises(PermissionError):
        runtime.safe_patch("app.py", "return 'old'", "return 'new'")

    # Valid patch inside scope
    runtime.init_contract(mode="implement", allowed_scope=["app.py"])
    result = runtime.safe_patch("app.py", "return 'old'", "return 'new'")
    assert "Successfully patched" in result
    assert "return 'new'" in target_file.read_text(encoding="utf-8")


def test_run_verification_on_clean_workspace(tmp_path: Path) -> None:
    """Verifies run_verification returns PASS on valid Python code."""
    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def test_func() -> int:\n    return 10\n", encoding="utf-8")

    res = run_verification(tier=1, workspace_dir=tmp_path)
    assert res["passed"] is True
    assert "VERDICT: PASS" in res["verdict"]

    # Introduce syntax error
    bad_file = tmp_path / "broken.py"
    bad_file.write_text("def broken(:\n    pass\n", encoding="utf-8")

    res_fail = run_verification(tier=1, workspace_dir=tmp_path)
    assert res_fail["passed"] is False
    assert "VERDICT: FAIL" in res_fail["verdict"]


def test_setup_opencode(tmp_path: Path) -> None:
    """Verifies that setup_opencode creates OPENCODE.md, agent md, agent json, and opencode.json."""
    created = setup_opencode(tmp_path)
    assert len(created) == 4

    opencode_md = tmp_path / "OPENCODE.md"
    assert opencode_md.exists()
    assert "HyperFlash Reliability Constitution for OpenCode" in opencode_md.read_text(encoding="utf-8")

    agent_md = tmp_path / ".opencode" / "agents" / "hyperflash.md"
    assert agent_md.exists()
    assert "HyperFlash Engineering Reliability Agent for OpenCode" in agent_md.read_text(encoding="utf-8")

    agent_json = tmp_path / ".opencode" / "agents" / "hyperflash.json"
    assert agent_json.exists()
    assert "HyperFlash" in agent_json.read_text(encoding="utf-8")

    opencode_json = tmp_path / "opencode.json"
    assert opencode_json.exists()
    content = opencode_json.read_text(encoding="utf-8")
    assert "mcpServers" in content
    assert "hyperflash" in content
    assert '"agent": "hyperflash"' in content


def test_setup_opencode_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that setup_opencode(is_global=True) writes to ~/.config/opencode/opencode.json and ~/.config/opencode/agents/hyperflash.md."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    created = setup_opencode(is_global=True)
    assert len(created) == 2

    expected_path = fake_home / ".config" / "opencode" / "opencode.json"
    assert str(expected_path) in created
    assert expected_path.exists()

    expected_agent = fake_home / ".config" / "opencode" / "agents" / "hyperflash.md"
    assert str(expected_agent) in created
    assert expected_agent.exists()
    assert "HyperFlash Engineering Reliability Agent for OpenCode" in expected_agent.read_text(encoding="utf-8")

    data = json.loads(expected_path.read_text(encoding="utf-8"))
    assert "agent" in data
    assert "hyperflash" in data["agent"]
    hf_agent = data["agent"]["hyperflash"]
    assert hf_agent["name"] == "HyperFlash"
    assert "Universal Engineering Reliability" in hf_agent["description"]
    assert "8 HyperFlash Invariants" in hf_agent["system"]

    assert "mcp" in data
    assert "servers" in data["mcp"]
    assert "hyperflash" in data["mcp"]["servers"]
    hf_server = data["mcp"]["servers"]["hyperflash"]
    assert hf_server["type"] == "local"
    assert hf_server["command"] == ["hyperflash", "mcp"]


def test_setup_opencode_global_merges_without_overwriting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that global config setup safely merges without deleting existing agents or servers."""
    fake_home = tmp_path / "home"
    config_dir = fake_home / ".config" / "opencode"
    config_dir.mkdir(parents=True)
    target_file = config_dir / "opencode.json"

    initial_config = {
        "agent": {
            "custom_coder": {
                "name": "Custom Coder",
                "system": "You write code."
            }
        },
        "mcp": {
            "servers": {
                "git_mcp": {
                    "type": "local",
                    "command": ["git-mcp"]
                }
            }
        },
        "custom_setting": True
    }
    target_file.write_text(json.dumps(initial_config), encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    created = setup_opencode(is_global=True)
    assert len(created) == 2

    data = json.loads(target_file.read_text(encoding="utf-8"))
    assert "custom_coder" in data["agent"]
    assert "hyperflash" in data["agent"]
    assert "git_mcp" in data["mcp"]["servers"]
    assert "hyperflash" in data["mcp"]["servers"]
    assert data["custom_setting"] is True


def test_setup_claude_workspace_and_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies setup_claude in both workspace and global modes."""
    # Workspace mode
    workspace = tmp_path / "ws"
    workspace.mkdir()
    ws_created = setup_claude(workspace, is_global=False)
    assert len(ws_created) == 5
    assert (workspace / "CLAUDE.md").exists()
    assert (workspace / ".claude" / "commands" / "hyperflash.md").exists()
    assert (workspace / ".claude" / "agents" / "hyperflash.md").exists()
    assert (workspace / ".claude.json").exists()
    assert (workspace / ".mcp.json").exists()

    # Global mode
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    global_created = setup_claude(is_global=True)
    assert len(global_created) == 4
    assert (fake_home / ".claude" / "CLAUDE.md").exists()
    assert (fake_home / ".claude" / "commands" / "hyperflash.md").exists()
    assert (fake_home / ".claude" / "agents" / "hyperflash.md").exists()
    assert (fake_home / ".claude.json").exists()


def test_setup_windsurf_workspace_and_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies setup_windsurf in both workspace and global modes."""
    # Workspace mode
    workspace = tmp_path / "ws"
    workspace.mkdir()
    ws_created = setup_windsurf(workspace, is_global=False)
    assert len(ws_created) == 3
    assert (workspace / ".windsurfrules").exists()
    assert (workspace / ".windsurf" / "rules" / "hyperflash.md").exists()
    assert (workspace / ".windsurf" / "mcp.json").exists()

    # Global mode
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)
    global_created = setup_windsurf(is_global=True)
    assert len(global_created) == 5
    assert (fake_home / ".codeium" / "windsurf" / "memories" / "global_rules.md").exists()
    assert (fake_home / ".codeium" / "windsurf" / "mcp_config.json").exists()
    assert (fake_home / ".windsurf" / "rules" / "hyperflash.md").exists()
    assert (fake_home / ".windsurf" / "mcp.json").exists()
    assert (fake_home / ".windsurfrules").exists()


def test_setup_cline_workspace_and_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies setup_cline in both workspace and global modes."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Workspace mode
    workspace = tmp_path / "ws"
    workspace.mkdir()
    ws_created = setup_cline(workspace, is_global=False)
    assert any(".clinerules" in f for f in ws_created)
    assert (workspace / ".clinerules").exists()

    # Global mode
    global_created = setup_cline(is_global=True)
    assert len(global_created) > 0
    assert (fake_home / ".clinerules").exists()
    assert (fake_home / ".cline" / "data" / "settings" / "cline_mcp_settings.json").exists()


def test_setup_roo_workspace_and_global(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies setup_roo in both workspace and global modes."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setattr(Path, "home", lambda: fake_home)

    # Workspace mode
    workspace = tmp_path / "ws"
    workspace.mkdir()
    ws_created = setup_roo(workspace, is_global=False)
    assert any(".roorules" in f for f in ws_created)
    assert (workspace / ".roorules").exists()

    # Global mode
    global_created = setup_roo(is_global=True)
    assert len(global_created) > 0
    assert (fake_home / ".roorules").exists()


def test_setup_git_hook_excludes_tests(tmp_path: Path) -> None:
    """Verifies that setup_git_hook generates pre-commit script excluding tests directory."""
    git_dir: Path = tmp_path / ".git"
    git_dir.mkdir()
    created: list[str] = setup_git_hook(tmp_path)
    assert len(created) == 1
    hook_file: Path = Path(created[0])
    assert hook_file.exists()
    hook_content: str = hook_file.read_text(encoding="utf-8")
    assert r"grep -vE '(^|/)tests?/'" in hook_content
    assert r"grep -vE '(^|/)tests?/'" in GIT_PRE_COMMIT_CONTENT


