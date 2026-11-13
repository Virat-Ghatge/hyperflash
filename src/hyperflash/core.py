"""
Core HyperFlash runtime logic: invariant enforcement, AST symbol graph generation,
contract state management, and hierarchical verification runner.
"""
from __future__ import annotations

import ast
import json
import py_compile
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

BANNED_ELISION_PATTERNS: list[str] = [
    r"//\s*\.\.\.\s*(rest|existing|unchanged|remaining|code)",
    r"#\s*\.\.\.\s*(rest|existing|unchanged|remaining|code)",
    r"/\*\s*\.\.\.\s*.*?\*/",
    r"TODO:\s*implement",
    r"//\s*\.\.\.\s*$",
    r"#\s*\.\.\.\s*$",
    r"/\*\s*existing code.*?\*/",
    r"<!--\s*\.\.\.\s*-->",
]

IGNORE_DIRS: set[str] = {
    ".git",
    ".agents",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
}

DEFAULT_CONTRACT: dict[str, Any] = {
    "mode": "implement",
    "effort_profile": "balanced",
    "planning": "compact",
    "context_depth": "dependency",
    "verification_depth": "impact",
    "delegation": "conditional",
    "reason_codes": [],
    "allowed_write_scope": [],
    "acceptance_criteria": [],
    "files_read_in_session": [],
    "last_mutation_ts": 0.0,
    "last_verified_ts": 0.0,
    "last_verdict": "PENDING",
}


def check_for_elision(text: str) -> tuple[bool, str]:
    """
    Scans text for prohibited lazy truncation and placeholder patterns.

    Returns:
        tuple[bool, str]: (True, matched_pattern) if elision found, else (False, "")
    """
    for pattern in BANNED_ELISION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return True, match.group(0)
    return False, ""


def enforce_elision_guard(text: str) -> None:
    """
    Raises ValueError if prohibited elision patterns are detected in the given text.
    """
    has_elision, pattern = check_for_elision(text)
    if has_elision:
        raise ValueError(
            f"Invariant 7 Violation (Code Truncation Blocked): Prohibited elision pattern '{pattern}' detected. "
            "HyperFlash requires 100% complete, fully implemented code with zero shortcuts."
        )


def index_python_source(source_code: str, file_label: str = "<source>") -> dict[str, Any]:
    """
    Parses Python source code into an AST and extracts structured symbol metadata.
    """
    try:
        tree = ast.parse(source_code, filename=file_label)
    except SyntaxError:
        return {}

    symbols: dict[str, Any] = {
        "classes": {},
        "functions": [],
        "imports": [],
    }

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            try:
                symbols["imports"].append(ast.unparse(node))
            except Exception:
                pass
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args: list[str] = [a.arg for a in node.args.args]
            ret_type: str = "Untyped"
            if node.returns is not None:
                try:
                    ret_type = ast.unparse(node.returns)
                except Exception:
                    ret_type = "Complex"
            prefix: str = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            symbols["functions"].append(
                f"L{node.lineno}: {prefix} {node.name}({', '.join(args)}) -> {ret_type}"
            )
        elif isinstance(node, ast.ClassDef):
            methods: list[str] = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    m_prefix: str = "async " if isinstance(item, ast.AsyncFunctionDef) else ""
                    m_args: list[str] = [a.arg for a in item.args.args]
                    m_ret: str = "Untyped"
                    if item.returns is not None:
                        try:
                            m_ret = ast.unparse(item.returns)
                        except Exception:
                            m_ret = "Complex"
                    methods.append(f"L{item.lineno}:{m_prefix}{item.name}({', '.join(m_args)}) -> {m_ret}")
            symbols["classes"][f"L{node.lineno}:{node.name}"] = methods

    return {k: v for k, v in symbols.items() if v}


def index_python_file(path: Path) -> dict[str, Any]:
    """
    Indexes a single Python file on disk into symbol metadata.
    """
    if not path.is_file():
        return {}
    try:
        content: str = path.read_text(encoding="utf-8", errors="ignore")
        return index_python_source(content, str(path))
    except Exception:
        return {}


def generate_symbol_graph(root_dir: Path | str = ".") -> dict[str, dict[str, Any]]:
    """
    Crawls root_dir and indexes all Python files into an AST symbol graph.
    """
    base_path = Path(root_dir).resolve()
    graph: dict[str, dict[str, Any]] = {}

    if not base_path.exists():
        return graph

    for py_file in base_path.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in py_file.parts):
            continue
        info = index_python_file(py_file)
        if info:
            try:
                rel_path = py_file.relative_to(base_path).as_posix()
            except ValueError:
                rel_path = py_file.as_posix()
            graph[rel_path] = info

    return graph


def build_symbol_graph(
    root_dir: Path | str = ".",
    output_file: Path | str = ".agents/state/symbol_graph.json",
) -> dict[str, dict[str, Any]]:
    """
    Generates symbol graph and writes it to output_file on disk.
    """
    base_path = Path(root_dir)
    out_path = Path(output_file) if Path(output_file).is_absolute() else base_path / output_file
    graph = generate_symbol_graph(base_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    return graph


def load_contract(
    contract_path: Path | str = ".agents/state/contract.json",
) -> dict[str, Any]:
    """
    Loads contract state safely from JSON file, returning DEFAULT_CONTRACT on error.
    """
    path = Path(contract_path)
    if not path.is_file():
        return dict(DEFAULT_CONTRACT)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_CONTRACT)
        merged.update(data)
        return merged
    except Exception:
        return dict(DEFAULT_CONTRACT)


def save_contract(
    contract_data: dict[str, Any],
    contract_path: Path | str = ".agents/state/contract.json",
) -> None:
    """
    Safely serializes and saves contract data to contract_path.
    """
    path = Path(contract_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(contract_data, indent=2), encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str]:
    """
    Executes a shell command safely, capturing stdout and stderr.
    """
    try:
        res = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        combined: str = (res.stdout + "\n" + res.stderr).strip()
        truncated: str = combined[-4000:] if len(combined) > 4000 else combined
        return res.returncode, truncated
    except Exception as exc:
        return 1, str(exc)


def run_verification(
    tier: int | None = None,
    custom_cmd: str = "",
    workspace_dir: Path | str = ".",
) -> dict[str, Any]:
    """
    Executes the HyperFlash deterministic verification hierarchy and updates contract.json.
    """
    workspace = Path(workspace_dir).resolve()
    contract_path = workspace / ".agents/state/contract.json"
    diagnostics: list[dict[str, Any]] = []
    passed_all: bool = True

    def tier_active(t: int) -> bool:
        return tier is None or t <= tier

    # Gather Python source files
    py_files: list[Path] = [
        p for p in workspace.rglob("*.py")
        if not any(part in IGNORE_DIRS for part in p.parts)
    ]

    # Tier 1: Syntax Integrity (py_compile)
    if tier_active(1) and py_files:
        for py_f in py_files:
            try:
                py_compile.compile(str(py_f), doraise=True)
            except py_compile.PyCompileError as err:
                passed_all = False
                diagnostics.append({
                    "tier": 1,
                    "name": "syntax_integrity",
                    "tool": "py_compile",
                    "file": str(py_f.relative_to(workspace) if py_f.is_relative_to(workspace) else py_f),
                    "error": str(err),
                })

    # Tier 3: Static Type Soundness (tsc / mypy)
    if tier_active(3):
        tsconfig = workspace / "tsconfig.json"
        if tsconfig.exists() and shutil.which("npx"):
            code, out = run_cmd(["npx", "tsc", "--noEmit"], cwd=workspace)
            diagnostics.append({
                "tier": 3,
                "name": "type_soundness",
                "tool": "tsc",
                "exit_code": code,
                "output": out,
            })
            if code != 0:
                passed_all = False

    # Tier 5: Static Analysis / Linting (ruff)
    if tier_active(5) and py_files and shutil.which("ruff"):
        code, out = run_cmd(["ruff", "check", "."], cwd=workspace)
        diagnostics.append({
            "tier": 5,
            "name": "static_analysis",
            "tool": "ruff",
            "exit_code": code,
            "output": out,
        })
        if code != 0:
            passed_all = False

    # Tier 6: Workspace Test Suite (pytest)
    has_py_tests = any(p.name.startswith("test_") or p.name.endswith("_test.py") for p in py_files)
    if tier_active(6) and has_py_tests and shutil.which("pytest"):
        code, out = run_cmd(["pytest", "-q", "--tb=short"], cwd=workspace)
        diagnostics.append({
            "tier": 6,
            "name": "workspace_test_suite",
            "tool": "pytest",
            "exit_code": code,
            "output": out,
        })
        if code != 0:
            passed_all = False

    # Custom Command if provided
    if custom_cmd:
        code, out = run_cmd(custom_cmd.split(), cwd=workspace)
        diagnostics.append({
            "tier": 0,
            "name": "custom_validator",
            "command": custom_cmd,
            "exit_code": code,
            "output": out,
        })
        if code != 0:
            passed_all = False

    verdict_str: str = "VERDICT: PASS" if passed_all else "VERDICT: FAIL -- Verification checks failed"

    # Update contract state
    contract = load_contract(contract_path)
    if passed_all:
        contract["last_verified_ts"] = time.time()
        contract["last_verdict"] = "PASS"
    else:
        contract["last_verdict"] = "FAIL"
    save_contract(contract, contract_path)

    return {
        "verdict": verdict_str,
        "passed": passed_all,
        "diagnostics": diagnostics,
        "timestamp": time.time(),
    }


class HyperFlashRuntime:
    """
    High-level API for interacting with HyperFlash runtime within Python.
    """

    def __init__(self, workspace_dir: Path | str = ".") -> None:
        self.workspace_dir: Path = Path(workspace_dir).resolve()
        self.contract_path: Path = self.workspace_dir / ".agents/state/contract.json"
        self.symbol_graph_path: Path = self.workspace_dir / ".agents/state/symbol_graph.json"

    def get_contract(self) -> dict[str, Any]:
        """Returns active contract state."""
        return load_contract(self.contract_path)

    def init_contract(
        self,
        mode: str = "implement",
        allowed_scope: list[str] | None = None,
        acceptance_criteria: list[str] | None = None,
        effort_profile: str = "balanced",
    ) -> dict[str, Any]:
        """Initializes or overwrites contract state."""
        contract = load_contract(self.contract_path)
        contract["mode"] = mode
        contract["effort_profile"] = effort_profile
        contract["allowed_write_scope"] = allowed_scope or []
        contract["acceptance_criteria"] = acceptance_criteria or []
        contract["last_verdict"] = "PENDING"
        save_contract(contract, self.contract_path)
        return contract

    def generate_symbol_graph(self) -> dict[str, dict[str, Any]]:
        """Re-indexes workspace AST symbol graph and stores to disk."""
        return build_symbol_graph(self.workspace_dir, self.symbol_graph_path)

    def verify(self, tier: int | None = None, custom_cmd: str = "") -> dict[str, Any]:
        """Executes verification hierarchy."""
        return run_verification(tier=tier, custom_cmd=custom_cmd, workspace_dir=self.workspace_dir)

    def safe_patch(self, target_file: str, search_text: str, replacement_text: str) -> str:
        """
        Applies surgical search-and-replace edit with Invariant 7 (Zero Elision)
        and Invariant 2 (Scope Confinement) validation.
        """
        # Invariant 7: Elision guard
        enforce_elision_guard(replacement_text)

        target_path = (self.workspace_dir / target_file).resolve()
        norm_target = str(target_path.as_posix())

        # Invariant 2: Scope Confinement
        contract = self.get_contract()
        allowed_scope = [str(Path(p).as_posix()) for p in contract.get("allowed_write_scope", [])]
        if allowed_scope:
            if not any(norm_target.endswith(s) or s in norm_target for s in allowed_scope):
                raise PermissionError(
                    f"Invariant 2 Violation (Out of Scope): '{target_file}' is outside allowed_write_scope {allowed_scope}."
                )

        if not target_path.exists():
            raise FileNotFoundError(f"Target file '{target_file}' does not exist.")

        content = target_path.read_text(encoding="utf-8")
        if search_text not in content:
            raise ValueError(f"Search text not found in '{target_file}'.")

        new_content = content.replace(search_text, replacement_text, 1)
        target_path.write_text(new_content, encoding="utf-8")

        contract["last_mutation_ts"] = time.time()
        save_contract(contract, self.contract_path)
        return f"Successfully patched '{target_file}'."
