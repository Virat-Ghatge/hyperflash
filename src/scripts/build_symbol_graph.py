#!/usr/bin/env python3
"""SessionStart Hook: Generates compact AST symbol_graph.json in the active workspace."""
import ast
import json
import sys
from pathlib import Path

IGNORE_DIRS = {".git", ".agents", "node_modules", "__pycache__", ".venv", "venv", "build", "dist"}
OUTPUT_FILE = Path(".agents/state/symbol_graph.json")

def index_python_file(path: Path) -> dict:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return {}
    symbols: dict = {"classes": {}, "functions": [], "imports": []}
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            symbols["imports"].append(ast.unparse(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            ret = ast.unparse(node.returns) if node.returns else "Untyped"
            symbols["functions"].append(f"L{node.lineno}: {node.name}({', '.join(args)}) -> {ret}")
        elif isinstance(node, ast.ClassDef):
            methods = [
                f"L{m.lineno}:{m.name}"
                for m in node.body
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            symbols["classes"][f"L{node.lineno}:{node.name}"] = methods
    return {k: v for k, v in symbols.items() if v}

def main() -> None:
    try:
        graph = {}
        for py_file in Path(".").rglob("*.py"):
            if any(part in IGNORE_DIRS for part in py_file.parts):
                continue
            info = index_python_file(py_file)
            if info:
                graph[str(py_file.as_posix())] = info
        if graph:
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_FILE.write_text(json.dumps(graph, indent=2), encoding="utf-8")
    except Exception:
        pass
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
