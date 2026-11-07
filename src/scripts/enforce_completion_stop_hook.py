#!/usr/bin/env python3
"""
Stop Hook for HYPERFLASH:
Enforces Invariant 3 (Completion needs fresh evidence).
If source files were mutated in this session (last_mutation_ts > last_verified_ts),
blocks the agent from stopping until verify_hierarchy.py passes.
"""
import json
import sys
from pathlib import Path

CONTRACT_PATH = Path(".agents/state/contract.json")

def main() -> None:
    if not CONTRACT_PATH.exists():
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    except Exception:
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    last_mut = float(contract.get("last_mutation_ts", 0.0))
    last_ver = float(contract.get("last_verified_ts", 0.0))
    verdict = contract.get("last_verdict", "PENDING")

    if last_mut > 0 and (last_ver < last_mut or verdict != "PASS"):
        print(json.dumps({
            "decision": "deny",
            "reason": (
                "[HYPERFLASH INVARIANT 3 GATE] Source files were mutated since the last passing verification "
                f"(last_verdict={verdict}). You MUST invoke 'hyperflash-test-adversary' or run "
                "'python3 ~/.gemini/config/skills/hyperflash/scripts/verify_hierarchy.py' "
                "and achieve VERDICT: PASS before completing the response."
            )
        }))
        sys.exit(0)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
