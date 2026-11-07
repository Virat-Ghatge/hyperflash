#!/usr/bin/env python3
"""CLI helper to initialize or amend .agents/state/contract.json in the active workspace."""
import argparse
import json
import time
from pathlib import Path

CONTRACT_PATH = Path(".agents/state/contract.json")

def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize or update HyperFlash contract.json")
    parser.add_argument("--mode", default="implement", choices=["answer", "research", "plan", "review", "security-review", "implement", "debug", "migration"])
    parser.add_argument("--effort", default="balanced", choices=["eco", "balanced", "deep"])
    parser.add_argument("--planning", default="compact", choices=["direct", "compact", "deep", "replan"])
    parser.add_argument("--context-depth", default="dependency")
    parser.add_argument("--verification-depth", default="impact")
    parser.add_argument("--delegation", default="conditional")
    parser.add_argument("--scope", nargs="*", default=[], help="List of allowed file paths or directory prefixes")
    parser.add_argument("--criteria", nargs="*", default=["All checks and tests pass"], help="Acceptance criteria")
    parser.add_argument("--reasons", nargs="*", default=["standard-task"], help="Reason codes")
    args = parser.parse_args()

    existing = {}
    if CONTRACT_PATH.exists():
        try:
            existing = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        except Exception:
            existing = {}

    contract = {
        "mode": args.mode,
        "effort_profile": args.effort,
        "planning": args.planning,
        "context_depth": args.context_depth,
        "verification_depth": args.verification_depth,
        "delegation": args.delegation,
        "reason_codes": args.reasons,
        "allowed_write_scope": args.scope if args.scope else existing.get("allowed_write_scope", []),
        "acceptance_criteria": args.criteria if args.criteria else existing.get("acceptance_criteria", []),
        "files_read_in_session": existing.get("files_read_in_session", []),
        "last_mutation_ts": existing.get("last_mutation_ts", 0.0),
        "last_verified_ts": existing.get("last_verified_ts", time.time()),
        "last_verdict": existing.get("last_verdict", "PENDING"),
    }

    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(json.dumps(contract, indent=2), encoding="utf-8")
    print(json.dumps({"status": "CONTRACT_UPDATED", "contract": contract}, indent=2))

if __name__ == "__main__":
    main()
