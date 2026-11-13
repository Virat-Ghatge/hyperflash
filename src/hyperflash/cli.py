"""
CLI entry point for HyperFlash:
Commands: init, mcp, verify, decide, status, --version.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from hyperflash import __version__
from hyperflash.core import (
    generate_symbol_graph,
    load_contract,
    run_verification,
    save_contract,
)
from hyperflash.mcp_server import run_stdio_server
from hyperflash.polyglot import (
    setup_all,
    setup_antigravity,
    setup_claude,
    setup_cline,
    setup_cursor,
    setup_git_hooks,
    setup_opencode,
    setup_roo,
    setup_windsurf,
)


def cmd_init(args: argparse.Namespace) -> int:
    """Handles 'hyperflash init' command."""
    target: str = args.target.lower()
    workspace: str = args.workspace
    is_global: bool = getattr(args, "is_global", False)

    target_desc: str = "globally in user home" if is_global else f"in '{workspace}'"
    print(f"⚡ HyperFlash: Initializing reliability runtime for target '{target}' {target_desc}...")

    if target == "all":
        results = setup_all(workspace, is_global=is_global)
        for platform, files in results.items():
            print(f"  • {platform.capitalize()}:")
            for f in files:
                print(f"    - Configured: {f}")
    elif target == "cursor":
        files = setup_cursor(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Cursor: {f}")
    elif target == "claude":
        files = setup_claude(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Claude Code: {f}")
    elif target == "windsurf":
        files = setup_windsurf(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Windsurf: {f}")
    elif target == "git":
        files = setup_git_hooks(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Git pre-commit hook: {f}")
    elif target == "antigravity":
        files = setup_antigravity(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Antigravity: {f}")
    elif target == "opencode":
        files = setup_opencode(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured OpenCode: {f}")
    elif target == "cline":
        files = setup_cline(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Cline: {f}")
    elif target == "roo":
        files = setup_roo(workspace, is_global=is_global)
        for f in files:
            print(f"  • Configured Roo Code: {f}")
    else:
        print(f"❌ Unknown target '{target}'. Choose from all, cursor, claude, windsurf, git, antigravity, opencode, cline, roo.")
        return 1

    print("✅ HyperFlash initialization complete. Guardrails are active.")
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    """Handles 'hyperflash mcp' command."""
    workspace: str = getattr(args, "workspace", ".")
    run_stdio_server(workspace_dir=workspace)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Handles 'hyperflash verify' command."""
    tier: int | None = args.tier
    custom_cmd: str = args.custom_cmd or ""
    workspace: str = args.workspace

    print(f"⚡ Running HyperFlash verification (tier: {tier or 'all'}, custom: '{custom_cmd}')...")
    res = run_verification(tier=tier, custom_cmd=custom_cmd, workspace_dir=workspace)

    verdict: str = res.get("verdict", "VERDICT: UNKNOWN")
    diagnostics = res.get("diagnostics", [])

    print("\n" + json.dumps({"diagnostics": diagnostics, "verdict": verdict}, indent=2))
    print(f"\n{verdict}")

    return 0 if res.get("passed", False) else 1


def cmd_decide(args: argparse.Namespace) -> int:
    """Handles 'hyperflash decide' command."""
    workspace = Path(args.workspace).resolve()
    contract_path = workspace / ".agents/state/contract.json"
    contract = load_contract(contract_path)

    contract["mode"] = args.mode
    if args.scope:
        contract["allowed_write_scope"] = args.scope
    if args.criteria:
        contract["acceptance_criteria"] = args.criteria
    contract["last_verdict"] = "PENDING"

    save_contract(contract, contract_path)
    print(f"✅ HyperFlash Contract Updated at {contract_path.as_posix()}:")
    print(f"  • Mode: {contract['mode']}")
    print(f"  • Allowed Scope: {contract['allowed_write_scope']}")
    print(f"  • Criteria: {contract['acceptance_criteria']}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Handles 'hyperflash status' command."""
    workspace = Path(args.workspace).resolve()
    contract_path = workspace / ".agents/state/contract.json"
    contract = load_contract(contract_path)
    graph = generate_symbol_graph(workspace)

    print("⚡ HYPERFLASH RUNTIME STATUS")
    print("=" * 50)
    print(f"Workspace: {workspace.as_posix()}")
    print(f"Active Mode: {contract.get('mode', 'uninitialized')}")
    print(f"Effort Profile: {contract.get('effort_profile', 'balanced')}")
    print(f"Allowed Scope: {contract.get('allowed_write_scope', [])}")
    print(f"Acceptance Criteria: {len(contract.get('acceptance_criteria', []))} defined")
    for idx, c in enumerate(contract.get("acceptance_criteria", []), 1):
        print(f"   {idx}. {c}")
    print(f"Last Verdict: {contract.get('last_verdict', 'NONE')}")
    print(f"Last Verified TS: {contract.get('last_verified_ts', 0.0)}")
    print(f"Last Mutation TS: {contract.get('last_mutation_ts', 0.0)}")
    print(f"AST Indexed Files: {len(graph)} Python modules")
    print("=" * 50)
    return 0


def cmd_check_elision(args: argparse.Namespace) -> int:
    """Handles 'hyperflash check-elision' command for pre-commit hook."""
    from hyperflash.core import check_for_elision

    files: list[str] = args.files
    failed: bool = False
    for file_str in files:
        p = Path(file_str)
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            has_elision, pattern = check_for_elision(content)
            if has_elision:
                print(f"❌ [HYPERFLASH ERROR] Code elision detected in '{file_str}': matched '{pattern}'")
                failed = True
        except Exception:
            pass

    if failed:
        print("❌ HyperFlash Zero-Elision Guard: Prohibited truncation comments detected.")
        return 1
    return 0


def cmd_launch(args: argparse.Namespace) -> int:
    """Handles 'hyperflash launch' command."""
    harness: str = args.harness.lower()
    extra_args: list[str] = list(getattr(args, "extra_args", []) or [])

    cmd_map: dict[str, list[str]] = {
        "opencode": ["opencode"],
        "antigravity": ["agy", "--agent", "hyperflash"],
        "agy": ["agy", "--agent", "hyperflash"],
        "claude": ["claude"],
        "cursor": ["cursor", "."],
        "windsurf": ["windsurf", "."],
    }

    base_cmd = cmd_map.get(harness)
    if not base_cmd:
        print(f"❌ Unknown harness '{harness}'. Choose from opencode, claude, cursor, windsurf, antigravity, agy.")
        return 1

    binary_name: str = base_cmd[0]
    resolved: str | None = shutil.which(binary_name)
    if not resolved and os.name == "nt":
        for ext in [".cmd", ".exe", ".bat", ".ps1"]:
            resolved = shutil.which(f"{binary_name}{ext}")
            if resolved:
                break

    if not resolved:
        print(f"❌ Harness '{harness}' not found in PATH. Please install it first.")
        return 1

    full_cmd: list[str] = [resolved or binary_name] + base_cmd[1:] + extra_args
    try:
        proc = subprocess.run(full_cmd, shell=(os.name == "nt"))
        return proc.returncode
    except FileNotFoundError:
        print(f"❌ Harness '{harness}' not found in PATH. Please install it first.")
        return 1
    except Exception as exc:
        print(f"❌ Error launching '{harness}': {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    """Constructs the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="hyperflash",
        description="HyperFlash: Universal Engineering Reliability Runtime & Multi-Agent Guardrails",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init
    p_init = subparsers.add_parser("init", help="1-Click setup for Cursor, Claude Code, Windsurf, Git hooks, Antigravity, OpenCode, Cline, Roo Code")
    p_init.add_argument(
        "--target",
        choices=["all", "cursor", "claude", "windsurf", "git", "antigravity", "opencode", "cline", "roo"],
        default="all",
        help="Target platform to configure (default: all)",
    )
    p_init.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: .)",
    )
    p_init.add_argument(
        "-g",
        "--global",
        dest="is_global",
        action="store_true",
        help="Configure globally in user home directory across all workspaces",
    )

    # launch
    p_launch = subparsers.add_parser("launch", help="Launch your preferred coding harness with HyperFlash agent active")
    p_launch.add_argument(
        "harness",
        choices=["opencode", "claude", "cursor", "windsurf", "antigravity", "agy"],
        help="Target harness",
    )
    p_launch.add_argument(
        "extra_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments forwarded to harness",
    )

    # mcp
    p_mcp = subparsers.add_parser("mcp", help="Launch stdio MCP server for universal tool integration")
    p_mcp.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: .)",
    )

    # verify
    p_verify = subparsers.add_parser("verify", help="Execute 9-tier deterministic verification hierarchy")
    p_verify.add_argument(
        "--tier",
        type=int,
        default=6,
        help="Maximum tier to run (1-9, default: 6)",
    )
    p_verify.add_argument(
        "--custom-cmd",
        type=str,
        default="",
        help="Optional custom command to validate",
    )
    p_verify.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: .)",
    )

    # decide
    p_decide = subparsers.add_parser("decide", help="Initialize or amend contract.json mode and write scope")
    p_decide.add_argument(
        "--mode",
        choices=["implement", "fix", "refactor", "direct", "review", "research"],
        default="implement",
        help="Execution mode (default: implement)",
    )
    p_decide.add_argument(
        "--scope",
        nargs="*",
        default=[],
        help="Allowed write scope file paths or directories",
    )
    p_decide.add_argument(
        "--criteria",
        nargs="*",
        default=[],
        help="Acceptance criteria items",
    )
    p_decide.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: .)",
    )

    # status
    p_status = subparsers.add_parser("status", help="Print active contract, AST graph, and verification status")
    p_status.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: .)",
    )

    # check-elision (for pre-commit hooks)
    p_check_elision = subparsers.add_parser("check-elision", help="Audit files for banned code truncation comments")
    p_check_elision.add_argument(
        "files",
        nargs="*",
        default=[],
        help="Files to audit for elision patterns",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """CLI main entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch: dict[str, Any] = {
        "init": cmd_init,
        "mcp": cmd_mcp,
        "verify": cmd_verify,
        "decide": cmd_decide,
        "status": cmd_status,
        "check-elision": cmd_check_elision,
        "launch": cmd_launch,
    }

    handler = dispatch.get(args.command)
    if handler:
        code: int = handler(args)
        sys.exit(code)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
