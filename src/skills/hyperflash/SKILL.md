---
name: hyperflash
description: >
  Use for software implementation, debugging, refactoring, review, migration,
  and other repository-changing engineering work where correctness must be
  verified. Enforces the 8 HyperFlash Invariants (scoped reconnaissance, adaptive
  planning, evidence-backed 9-tier verification, requirement tracking, failure
  recovery, zero-truncation completeness, exhaustive typing, and budget-aware
  subagent delegation).
license: MIT
---

# HYPERFLASH -- Engineering Reliability & Anti-Drift Runtime

**One rule above all:** Report what actually happened, not what you intended.
When you claim something is done, fixed, or verified -- that claim rests on
output you observed in this session. If you did not check, say you did not
check.

---

## THE 8 INVARIANTS

These hold across models and hosts. The global runtime enforces the
machine-checkable ones at the hook level (`~/.gemini/config/hooks.json`);
the rest are on you.

1. **Ground before mutating.** Read `.agents/state/symbol_graph.json`, then read
   the target file, its tests, and its callers via `view_file` before editing.
   Never act on assumed file state.
2. **Stay in declared scope.** Writes outside `allowed_write_scope` in
   `.agents/state/contract.json` are denied. If the scope is wrong, amend the
   contract via `hyperflash_decide.py` -- never route around it.
3. **Completion needs fresh evidence.** A criterion is done only when a
   HyperFlash-owned validator (`verify_hierarchy.py`) passed *after* the last
   relevant file mutation (`last_verified_ts >= last_mutation_ts`). Stale
   evidence and self-review do not count.
4. **Never exact-retry a failure.** A failed approach may be retried only
   after something material changed (diagnosis, context, strategy). The
   runtime blocks byte-identical retries via `.agents/state/retry_ledger.json`.
5. **Satisfy the contract.** Acceptance criteria and required validators in
   `.agents/state/contract.json` gate completion. Generic "tests passed" does
   not cover unrelated criteria.
6. **Say what you can't verify.** Mark uncertain or unverifiable claims
   explicitly. Downgrade confidence instead of fabricating certainty.
7. **Zero code elision & Chunked Long-Decode.** Never write `// ... rest of code`,
   `# ... existing implementation`, `/* unchanged */`, or `TODO: implement`.
   For edits exceeding 200 lines, use **Chunked Long-Decode**: write typed
   skeletons first, then populate implementation bodies in 100-150 line batches.
8. **Exhaustive static typing & Counterfactual Pre-Mortem.** Every function
   parameter and return signature must carry explicit static types. Always emit
   a `pre_mortem` block verifying callers and edge cases before mutating code.

---

## POLICY RECORD

Before multi-file or risky work, emit and persist the planning-policy record by
running `python3 ~/.gemini/config/skills/hyperflash/scripts/hyperflash_decide.py`:

```json
{
  "mode": "implement",
  "effort_profile": "balanced",
  "planning": "compact",
  "context_depth": "dependency",
  "verification_depth": "impact",
  "delegation": "none",
  "reason_codes": ["multiple-files", "shared-module"],
  "allowed_write_scope": ["src/core/engine.py", "tests/test_engine.py"],
  "acceptance_criteria": ["Engine handles empty buffer without raising ValueError"]
}
```

---

## MODES

| Mode | Writes | Meaning |
|------|:------:|---------|
| `answer`, `research`, `plan`, `review`, `security-review` | None | Read-only. Hooks deny writes and non-query shell. |
| `implement`, `debug` | Scoped | Normal work inside `allowed_write_scope`. |
| `migration` | Confirmed | Destructive-risk work. User checkpoint required. |

---

## VERIFICATION HIERARCHY

Execute verification via `python3 ~/.gemini/config/skills/hyperflash/scripts/verify_hierarchy.py`.
Prefer executable evidence over prose, in this order:

1. Hidden deterministic acceptance validator
2. External integration / runtime execution
3. Project tests (`pytest`, `jest`, `vitest`, `cargo test`, `go test`)
4. Compiler / type checker (`mypy`, `pyright`, `tsc --noEmit`, `py_compile`)
5. Deterministic static analysis (`ruff`, `eslint`)
6. Executable reproducer
7. Structural / diff invariant
8. Independent subagent review (`hyperflash-reviewer` / `hyperflash-test-adversary`)
9. Same-model self-review (supplementary only -- never completion evidence)

Every verification ends with:
`VERDICT: PASS`
or
`VERDICT: FAIL -- [reason] with failing output`
