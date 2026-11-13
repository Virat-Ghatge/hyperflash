"""
Unit tests for hyperflash.cli module:
Verifies subcommands: init, launch, verify, decide, status, check-elision, and --version.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hyperflash.cli import (
    build_parser,
    cmd_check_elision,
    cmd_decide,
    cmd_init,
    cmd_launch,
    cmd_status,
    cmd_verify,
)
from hyperflash.core import load_contract


def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that the --version flag outputs the current version and exits."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "hyperflash 1.1.1" in captured.out


def test_cli_decide_updates_contract(tmp_path: Path) -> None:
    """Verifies that 'hyperflash decide' modifies the contract accurately."""
    parser = build_parser()
    args = parser.parse_args([
        "decide",
        "--mode", "fix",
        "--scope", "src/auth.py", "tests/test_auth.py",
        "--criteria", "Pass all auth unit tests",
        "--workspace", str(tmp_path),
    ])

    exit_code = cmd_decide(args)
    assert exit_code == 0

    contract_path = tmp_path / ".agents" / "state" / "contract.json"
    contract = load_contract(contract_path)
    assert contract["mode"] == "fix"
    assert contract["allowed_write_scope"] == ["src/auth.py", "tests/test_auth.py"]
    assert contract["acceptance_criteria"] == ["Pass all auth unit tests"]


def test_cli_status_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that 'hyperflash status' prints active runtime metadata."""
    parser = build_parser()
    args = parser.parse_args(["status", "--workspace", str(tmp_path)])
    exit_code = cmd_status(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "HYPERFLASH RUNTIME STATUS" in captured.out
    assert "Active Mode:" in captured.out


def test_cli_init_cursor(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target cursor' scaffolds .cursorrules, rules mdc, and mcp.json."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "cursor", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    rules_file = tmp_path / ".cursorrules"
    assert rules_file.exists()
    assert "HyperFlash Engineering Rules" in rules_file.read_text(encoding="utf-8")

    mdc_file = tmp_path / ".cursor" / "rules" / "hyperflash.mdc"
    assert mdc_file.exists()
    assert "HyperFlash Engineering Reliability Agent for Cursor" in mdc_file.read_text(encoding="utf-8")

    mcp_file = tmp_path / ".cursor" / "mcp.json"
    assert mcp_file.exists()
    mcp_json = json.loads(mcp_file.read_text(encoding="utf-8"))
    assert "hyperflash" in mcp_json["mcpServers"]


def test_cmd_init_claude(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target claude' scaffolds CLAUDE.md, slash command, and .claude.json."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "claude", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    claude_md = tmp_path / "CLAUDE.md"
    assert claude_md.exists()
    assert "HyperFlash Reliability Constitution for Claude Code" in claude_md.read_text(encoding="utf-8")

    cmd_file = tmp_path / ".claude" / "commands" / "hyperflash.md"
    assert cmd_file.exists()
    assert "Activate HyperFlash Autonomous Engineering Reliability Agent" in cmd_file.read_text(encoding="utf-8")

    claude_json = tmp_path / ".claude.json"
    assert claude_json.exists()
    data = json.loads(claude_json.read_text(encoding="utf-8"))
    assert "hyperflash" in data["mcpServers"]


def test_cmd_init_windsurf(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target windsurf' scaffolds rules, rule md, and mcp.json."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "windsurf", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    rules_file = tmp_path / ".windsurfrules"
    assert rules_file.exists()
    assert "HyperFlash Engineering Rules for Windsurf" in rules_file.read_text(encoding="utf-8")

    rule_md = tmp_path / ".windsurf" / "rules" / "hyperflash.md"
    assert rule_md.exists()
    assert "HyperFlash Engineering Reliability Agent for Windsurf" in rule_md.read_text(encoding="utf-8")

    mcp_file = tmp_path / ".windsurf" / "mcp.json"
    assert mcp_file.exists()
    data = json.loads(mcp_file.read_text(encoding="utf-8"))
    assert "hyperflash" in data["mcpServers"]


def test_cmd_init_opencode(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target opencode' scaffolds OPENCODE.md, agent persona, and opencode.json."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "opencode", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    opencode_md = tmp_path / "OPENCODE.md"
    assert opencode_md.exists()
    assert "HyperFlash Reliability Constitution for OpenCode" in opencode_md.read_text(encoding="utf-8")

    agent_file = tmp_path / ".opencode" / "agents" / "hyperflash.json"
    assert agent_file.exists()
    agent_data = json.loads(agent_file.read_text(encoding="utf-8"))
    assert agent_data["name"] == "HyperFlash"
    assert "hyperflash_safe_patch" in agent_data["tools"]

    opencode_json = tmp_path / "opencode.json"
    assert opencode_json.exists()
    config_data = json.loads(opencode_json.read_text(encoding="utf-8"))
    assert config_data["agent"] == "hyperflash"
    assert "hyperflash" in config_data["agents"]
    assert "hyperflash" in config_data["mcpServers"]


def test_cli_init_all(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target all' scaffolds files for all harnesses."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "all", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    assert (tmp_path / ".cursorrules").exists()
    assert (tmp_path / ".cursor" / "rules" / "hyperflash.mdc").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".claude" / "commands" / "hyperflash.md").exists()
    assert (tmp_path / ".windsurfrules").exists()
    assert (tmp_path / ".windsurf" / "rules" / "hyperflash.md").exists()
    assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()
    assert (tmp_path / "OPENCODE.md").exists()
    assert (tmp_path / ".opencode" / "agents" / "hyperflash.json").exists()
    assert (tmp_path / "opencode.json").exists()


def test_cli_launch_missing_harness(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that launching a harness not found in PATH returns 1 and friendly error."""
    parser = build_parser()
    args = parser.parse_args(["launch", "opencode"])

    with patch("shutil.which", return_value=None):
        exit_code = cmd_launch(args)
        assert exit_code == 1

    captured = capsys.readouterr()
    assert "Harness 'opencode' not found in PATH" in captured.out


def test_cli_launch_success_forwarding() -> None:
    """Verifies that cmd_launch constructs the proper harness command and forwards extra args."""
    parser = build_parser()

    cases: list[tuple[list[str], list[str]]] = [
        (["launch", "opencode", "--prompt", "fix it"], ["opencode", "--prompt", "fix it"]),
        (["launch", "antigravity", "--model", "gemini"], ["agy", "--agent", "hyperflash", "--model", "gemini"]),
        (["launch", "agy", "-i", "hello"], ["agy", "--agent", "hyperflash", "-i", "hello"]),
        (["launch", "claude"], ["claude"]),
        (["launch", "cursor", "--new-window"], ["cursor", ".", "--new-window"]),
        (["launch", "windsurf"], ["windsurf", "."]),
    ]

    for argv, expected_cmd in cases:
        args = parser.parse_args(argv)
        with patch("shutil.which", side_effect=lambda x: x), patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            code = cmd_launch(args)
            assert code == 0
            mock_run.assert_called_once_with(expected_cmd, shell=(os.name == "nt"))


def test_cli_launch_windows_cmd_resolution() -> None:
    """Verifies that cmd_launch on Windows resolves .cmd shims when bare binary is missing."""
    parser = build_parser()
    args = parser.parse_args(["launch", "opencode", "--prompt", "check"])

    def mock_which(cmd: str) -> str | None:
        if cmd == "opencode.cmd":
            return r"C:\npm\opencode.cmd"
        return None

    with (
        patch("hyperflash.cli.os.name", "nt"),
        patch("shutil.which", side_effect=mock_which),
        patch("subprocess.run") as mock_run,
    ):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc

        code = cmd_launch(args)
        assert code == 0
        mock_run.assert_called_once_with([r"C:\npm\opencode.cmd", "--prompt", "check"], shell=True)


def test_cli_check_elision_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that 'hyperflash check-elision' correctly exits 0 on clean code and 1 on elided code."""
    parser = build_parser()

    clean_file = tmp_path / "clean.py"
    clean_file.write_text("def run():\n    return 42\n", encoding="utf-8")

    args_clean = parser.parse_args(["check-elision", str(clean_file)])
    assert cmd_check_elision(args_clean) == 0

    dirty_file = tmp_path / "dirty.py"
    dirty_file.write_text("def run():\n    // ... rest of implementation\n", encoding="utf-8")

    args_dirty = parser.parse_args(["check-elision", str(dirty_file)])
    assert cmd_check_elision(args_dirty) == 1
    captured = capsys.readouterr()
    assert "Code elision detected" in captured.out


def test_cli_verify_command(tmp_path: Path) -> None:
    """Verifies 'hyperflash verify' execution through CLI handler."""
    good_file = tmp_path / "module.py"
    good_file.write_text("VALUE: int = 100\n", encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(["verify", "--tier", "1", "--workspace", str(tmp_path)])
    exit_code = cmd_verify(args)
    assert exit_code == 0
