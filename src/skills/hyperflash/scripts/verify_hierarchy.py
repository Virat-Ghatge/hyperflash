#!/usr/bin/env python3
"""
Executes HyperFlash's Verification Hierarchy (Syntax -> Typecheck -> Linter -> Unit Tests)
and updates .agents/state/contract.json with fresh verification timestamps and VERDICT.
"""
import argparse
import json
import py_compile
import shutil
import subprocess
import sys
import time
from pathlib import Path

CONTRACT_PATH = Path(".agents/state/contract.json")

def run_cmd(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out = (res.stdout + "\n" + res.stderr).strip()
        return res.returncode, out[-4000:] if len(out) > 4000 else out
    except Exception as exc:
        return 1, str(exc)

def should_run_tier(tier: int, max_tier: int | None) -> bool:
    return max_tier is None or tier <= max_tier

def main() -> None:
    parser = argparse.ArgumentParser(description="Run HyperFlash Verification Hierarchy")
    parser.add_argument("--tier", type=int, default=None, help="Optional maximum verification tier (1-9)")
    parser.add_argument("--custom-cmd", type=str, default="", help="Optional custom test command")
    args = parser.parse_args()

    diagnostics: list[dict] = []
    passed_all = True

    py_files = [
        p for p in Path(".").rglob("*.py")
        if not any(part in {".git", ".agents", "node_modules", ".venv", "venv", "__pycache__"} for part in p.parts)
    ]
    if should_run_tier(4, args.tier):
        for py_f in py_files:
            try:
                py_compile.compile(str(py_f), doraise=True)
            except py_compile.PyCompileError as err:
                passed_all = False
                diagnostics.append({"tier": "4_syntax", "tool": "py_compile", "file": str(py_f), "error": str(err)})

    if should_run_tier(5, args.tier) and py_files and shutil.which("ruff"):
        code, out = run_cmd(["ruff", "check", "."])
        diagnostics.append({"tier": "5_static_analysis", "tool": "ruff", "exit_code": code, "output": out})
        if code != 0:
            passed_all = False

    has_py_tests = any(p.name.startswith("test_") or p.name.endswith("_test.py") for p in py_files)
    if should_run_tier(3, args.tier) and has_py_tests and shutil.which("pytest"):
        code, out = run_cmd(["pytest", "-q", "--tb=short"])
        diagnostics.append({"tier": "3_project_tests", "tool": "pytest", "exit_code": code, "output": out})
        if code != 0:
            passed_all = False

    if should_run_tier(4, args.tier) and Path("tsconfig.json").exists() and shutil.which("npx"):
        code, out = run_cmd(["npx", "tsc", "--noEmit"])
        diagnostics.append({"tier": "4_typecheck", "tool": "tsc", "exit_code": code, "output": out})
        if code != 0:
            passed_all = False

    if should_run_tier(1, args.tier) and args.custom_cmd:
        code, out = run_cmd(args.custom_cmd.split())
        diagnostics.append({"tier": "1_custom_validator", "tool": args.custom_cmd, "exit_code": code, "output": out})
        if code != 0:
            passed_all = False

    verdict = "VERDICT: PASS" if passed_all else "VERDICT: FAIL -- Verification checks failed"

    if CONTRACT_PATH.exists():
        try:
            contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        except Exception:
            contract = {}
    else:
        contract = {}

    if passed_all:
        contract["last_verified_ts"] = time.time()
        contract["last_verdict"] = "PASS"
    else:
        contract["last_verdict"] = "FAIL"

    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2), encoding="utf-8")

    print(json.dumps({"diagnostics": diagnostics, "verdict": verdict}, indent=2))
    print(f"\n{verdict}")
    sys.exit(0 if passed_all else 1)

if __name__ == "__main__":
    main()
