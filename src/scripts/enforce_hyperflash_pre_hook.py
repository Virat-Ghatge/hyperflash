#!/usr/bin/env python3
"""
PreToolUse Hook for HYPERFLASH:
Enforces Invariant 1 (Read before write), Invariant 2 (Scope & Mode),
Invariant 4 (No byte-identical retry of failed calls), and Invariant 7 (Zero code truncation).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

CONTRACT_PATH = Path(".agents/state/contract.json")
LEDGER_PATH = Path(".agents/state/retry_ledger.json")

READ_TOOLS = {"view_file", "read_file"}
WRITE_TOOLS = {"replace_file_content", "multi_replace_file_content", "write_to_file"}
READ_ONLY_MODES = {"answer", "research", "plan", "review", "security-review"}

BANNED_ELISION_PATTERNS = [
    r"//\s*\.\.\.\s*(rest|existing|unchanged|remaining|code)",
    r"#\s*\.\.\.\s*(rest|existing|unchanged|remaining|code)",
    r"/\*\s*\.\.\.\s*.*?\*/",
    r"TODO:\s*implement",
]

def deny(reason: str) -> None:
    print(json.dumps({"decision": "deny", "reason": f"[HYPERFLASH RUNTIME BLOCK] {reason}"}))
    sys.exit(0)

def allow() -> None:
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        allow()

    tool_name = payload.get("toolName", "")
    tool_input = payload.get("toolInput", {})
    raw_input_str = json.dumps(tool_input, sort_keys=True)

    contract = load_json(CONTRACT_PATH, {
        "mode": "implement",
        "allowed_write_scope": [],
        "files_read_in_session": [],
        "last_mutation_ts": 0.0,
        "last_verified_ts": 0.0,
        "last_verdict": "PENDING"
    })
    ledger = load_json(LEDGER_PATH, {"failed_hashes": []})

    # Track read files for Invariant 1
    if tool_name in READ_TOOLS:
        target = tool_input.get("AbsolutePath") or tool_input.get("TargetFile") or tool_input.get("path", "")
        if target:
            norm_target = str(Path(target).as_posix())
            read_set = set(contract.get("files_read_in_session", []))
            read_set.add(norm_target)
            contract["files_read_in_session"] = sorted(read_set)
            save_json(CONTRACT_PATH, contract)
        allow()

    # Invariant 4: Block byte-identical retry of a known failed call
    call_hash = hashlib.sha256(f"{tool_name}:{raw_input_str}".encode("utf-8")).hexdigest()
    if call_hash in ledger.get("failed_hashes", []):
        deny(
            "Invariant 4 Violation (Exact-Retry Blocked): This identical tool call already failed. "
            "Gather new context or change your approach before retrying."
        )

    if tool_name in WRITE_TOOLS:
        target = tool_input.get("TargetFile") or tool_input.get("AbsolutePath") or tool_input.get("path", "")
        norm_target = str(Path(target).as_posix()) if target else ""

        # Always permit writes to state/temp/installer files
        if any(x in norm_target for x in [".agents/state/", "/tmp/", "install_hyperflash_global.py", "install_hyperflash_config.py"]):
            allow()

        # Check Mode
        mode = contract.get("mode", "implement")
        if mode in READ_ONLY_MODES:
            deny(f"Mode Violation: Active mode is '{mode}' (read-only). Run hyperflash_decide.py --mode implement first.")

        # Invariant 2: Check allowed_write_scope (if contract.json has been initialized with a scope)
        allowed_scope = [str(Path(p).as_posix()) for p in contract.get("allowed_write_scope", [])]
        if allowed_scope:
            if not any(norm_target.endswith(s) or s in norm_target for s in allowed_scope):
                deny(
                    f"Invariant 2 Violation (Out of Scope): '{norm_target}' is outside allowed_write_scope {allowed_scope}. "
                    "Amend contract.json via hyperflash_decide.py if scope grew."
                )

        # Invariant 1: Must read existing file before editing
        if target and Path(target).exists():
            files_read = contract.get("files_read_in_session", [])
            if not any(norm_target.endswith(r) or r.endswith(norm_target) for r in files_read):
                deny(
                    f"Invariant 1 Violation (Ground Before Mutating): You must read '{norm_target}' "
                    "using view_file in this session before mutating it."
                )

        # Invariant 7: Block code truncation / lazy placeholders
        for pattern in BANNED_ELISION_PATTERNS:
            if re.search(pattern, raw_input_str, re.IGNORECASE):
                deny(
                    f"Invariant 7 Violation (Code Truncation Blocked): Banned placeholder matching '{pattern}' "
                    "detected. Emit 100% complete, executable code."
                )

    allow()

if __name__ == "__main__":
    main()
