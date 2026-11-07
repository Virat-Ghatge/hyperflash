---
trigger: always_on
description: Enforces HyperFlash Policy Records, Decision Records, Pre-Mortems, and Evidence Output Formatting across all sessions.
---

# HyperFlash Always-On Protocol

For any repository-changing or multi-file engineering task:

1. **Initialize or Update Contract First:**
   Ensure `.agents/state/contract.json` exists in the project workspace with valid `mode`, `effort_profile`, `planning` (`direct` | `compact` | `deep` | `replan`), `allowed_write_scope`, and `acceptance_criteria`.
2. **Emit Decision + Pre-Mortem Record Before Edits:**
   Before invoking `replace_file_content`, `multi_replace_file_content`, or `write_to_file` on source files, output a `decision:` block containing `action`, `reason`, `evidence`, `pre_mortem` (`upstream_callers_checked`, `null_or_edge_case_handling`, `type_completeness_verified`), `risk`, and `allowed_by_contract`.
3. **Mandatory Closing Format for Non-Trivial Tasks:**
   Conclude with:
   - `## Policy & Contract Summary`
   - `## What Changed`
   - `## Evidence` (including `VERDICT: PASS` or `VERDICT: FAIL -- [reason]`)
   - `## Why`
