#!/usr/bin/env python3
"""
PostToolUse Hook for HYPERFLASH:
1. Updates last_mutation_ts in .agents/state/contract.json whenever a source file is edited.
2. Logs tool call SHA-256 hash into retry_ledger.json if a tool call returned an error.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

CONTRACT_PATH = Path(".agents/state/contract.json")
LEDGER_PATH = Path(".agents/state/retry_ledger.json")
WRITE_TOOLS = {"replace_file_content", "multi_replace_file_content", "write_to_file"}

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
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    tool_name = payload.get("toolName", "")
    tool_input = payload.get("toolInput", {})
    tool_response = str(payload.get("toolResponse", ""))

    # Record mutation timestamp for Invariant 3
    if tool_name in WRITE_TOOLS:
        target = tool_input.get("TargetFile") or tool_input.get("AbsolutePath") or tool_input.get("path", "")
        norm_target = str(Path(target).as_posix()) if target else ""
        if not any(x in norm_target for x in [".agents/state/", "/tmp/", "install_hyperflash_global.py", "install_hyperflash_config.py"]):
            contract = load_json(CONTRACT_PATH, {})
            contract["last_mutation_ts"] = time.time()
            contract["last_verdict"] = "DIRTY"
            save_json(CONTRACT_PATH, contract)

    # Track failed tool calls for Invariant 4
    if "error" in tool_response.lower() or "exception" in tool_response.lower() or "verdict: fail" in tool_response.lower():
        raw_input_str = json.dumps(tool_input, sort_keys=True)
        call_hash = hashlib.sha256(f"{tool_name}:{raw_input_str}".encode("utf-8")).hexdigest()
        ledger = load_json(LEDGER_PATH, {"failed_hashes": []})
        if call_hash not in ledger["failed_hashes"]:
            ledger["failed_hashes"].append(call_hash)
            save_json(LEDGER_PATH, ledger)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
