"""
Unit tests for hyperflash.cli module:
Verifies subcommands: init, verify, decide, status, check-elision, and --version.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from hyperflash.cli import build_parser, cmd_check_elision, cmd_decide, cmd_init, cmd_status, cmd_verify
from hyperflash.core import load_contract


def test_cli_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that the --version flag outputs the current version and exits."""
    parser = build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "hyperflash 1.0.0" in captured.out


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
    """Verifies that 'hyperflash init --target cursor' scaffolds .cursorrules and mcp.json."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "cursor", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    rules_file = tmp_path / ".cursorrules"
    assert rules_file.exists()
    assert "HyperFlash Engineering Rules" in rules_file.read_text(encoding="utf-8")

    mcp_file = tmp_path / ".cursor" / "mcp.json"
    assert mcp_file.exists()
    mcp_json = json.loads(mcp_file.read_text(encoding="utf-8"))
    assert "hyperflash" in mcp_json["mcpServers"]


def test_cli_init_all(tmp_path: Path) -> None:
    """Verifies that 'hyperflash init --target all' scaffolds files for all harnesses."""
    parser = build_parser()
    args = parser.parse_args(["init", "--target", "all", "--workspace", str(tmp_path)])
    exit_code = cmd_init(args)
    assert exit_code == 0

    assert (tmp_path / ".cursorrules").exists()
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".windsurfrules").exists()
    assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()


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
