# ⚡ HyperFlash

> High-rigor, production-grade multi-agent reliability runtime for **Google Antigravity**. Forces fast models like **Gemini 3.8 Flash** to deliver enterprise-grade engineering output without drift, lazy truncation comments, or broken builds.

HyperFlash replaces the default Antigravity `/boost` flow with deterministic OS-level lifecycle hooks, AST symbol indexing, and an 8-invariant verification pipeline inspired by the open-source **Gravitas** runtime.

---

## 🚀 Quick Start

### 1. Installation

#### Linux & macOS
```bash
git clone https://github.com/Virat-Ghatge/hyperflash.git ~/hyperflash
cd ~/hyperflash
chmod +x install.sh
./install.sh
```

#### Windows (PowerShell)
```powershell
git clone https://github.com/Virat-Ghatge/hyperflash.git "$HOME\hyperflash"
cd "$HOME\hyperflash"
.\install.ps1
```

### 2. Verify Installation

```bash
# Verify the skill and agents are available
agy --version
agy --agent hyperflash "verify setup"
```

---

## 💡 Why HyperFlash?

Fast frontier models like **Gemini 3.8 Flash** have exceptional reasoning capabilities and blazing inference speeds, but autonomous coding agents frequently succumb to standard failure modes during complex tasks:

1. **Lazy Code Truncation:** Emitting `// ... rest of code` or `# ... existing implementation` comments that silently delete source logic.
2. **Context Drift & Hallucination:** Attempting edits on imagined file contents without grounding against actual workspace dependencies or callers.
3. **Out-of-Scope Mutations:** Touching unrelated files across the workspace during bug fixes.
4. **Premature Completion Claims:** Declaring "Fixed and verified!" without ever executing tests after modifying code.
5. **Byte-Identical Retry Loops:** Retrying the exact same failed tool call repeatedly when encountering compilation or runtime errors.

**HyperFlash** eliminates these failure modes by enforcing deterministic **OS-level lifecycle hooks** and an **8-invariant reliability runtime** directly in the Antigravity agent loop.

---

## 🏛️ Architecture & Lifecycle Hooks

```
                ┌────────────────────────────────────────────────────────┐
                │             Agent Workspace Lifecycle                  │
                └──────────────────────────┬─────────────────────────────┘
                                           │
                        [SessionStart] (Hook)
                                           ▼
                 Generate AST Symbol Graph (.agents/state/symbol_graph.json)
                                           │
                                           ▼
                     Orchestrator: @hyperflash (Contract Init)
                     .agents/state/contract.json (Mode, Scope, Criteria)
                                           │
                                           ▼
                      PreToolUse Hook (Invariants 1, 2, 4, 7)
               ┌───────────────────────────┼───────────────────────────┐
               │                           │                           │
         [Invariant 1]               [Invariant 2]               [Invariant 7]
       Ground First: Must         Scope Control: Deny          Zero Elision: Deny
       view_file target           writes outside contract      "// ... rest of code"
               │                           │                           │
               └───────────────────────────┼───────────────────────────┘
                                           │
                                           ▼
                                 Tool Execution (Edits)
                                           │
                                           ▼
                     PostToolUse Hook: Mark Mutation (Dirty TS)
                                           │
                                           ▼
                        Subagent Verification Escalation
                    Tier 1-6: @hyperflash-test-adversary
                    Tier 7-8: @hyperflash-reviewer
                                           │
                                           ▼
                     Stop Hook (Invariant 3 Evidence Gate)
                Deny stop if files mutated without VERDICT: PASS
```

---

## 🛡️ The 8 Invariants

These hold across models and runtime environments. Machine-checkable invariants are enforced at the OS hook level (`hooks.json`); the rest are bound by the agent constitution (`AGENTS.md`):

1. **Ground before mutating:** Read `.agents/state/symbol_graph.json`, then inspect the target file, its tests, and callers via `view_file` before editing. Never act on assumed state.
2. **Stay in declared scope:** Writes outside `allowed_write_scope` in `.agents/state/contract.json` are denied by the `PreToolUse` hook.
3. **Completion needs fresh evidence:** A task is completed only when a HyperFlash validator (`verify_hierarchy.py`) passed *after* the last file mutation (`last_verified_ts >= last_mutation_ts`). Stale evidence and self-review do not count.
4. **Never exact-retry a failure:** A failed approach may be retried only after context or diagnosis changes. The `PreToolUse` hook blocks byte-identical retries via `.agents/state/retry_ledger.json`.
5. **Satisfy the contract:** Acceptance criteria and required validators in `contract.json` gate completion.
6. **Say what you can't verify:** Downgrade confidence instead of fabricating certainty. Explicitly report unverified claims.
7. **Zero code elision & Chunked Long-Decode:** Never write `// ... rest of code`, `# ... existing implementation`, or `TODO: implement`. For edits exceeding 200 lines, use **Chunked Long-Decode**: write typed skeletons first, then populate bodies in 100-150 line batches.
8. **Exhaustive static typing & Counterfactual Pre-Mortem:** Every function parameter and return type must carry explicit static types. Always emit a `pre_mortem` block verifying callers and edge cases before mutating code.

---

## 🤖 The HyperFlash Multi-Agent Team

HyperFlash includes 6 specialized agent personas orchestrated automatically or invokable directly in Antigravity:

| Agent | Role | Capabilities |
|---|---|---|
| **`@hyperflash`** | **Elite Orchestrator** | Coordinates end-to-end task lifecycle, policy routing, and subagent delegation. |
| **`@hyperflash-investigator`** | **Codebase Reconnaissance** | Read-only explorer for complex symbol search, dependency tracing, and grounding. |
| **`@hyperflash-impact-auditor`** | **Blast Radius Auditor** | Maps caller chains, imports, and downstream contracts affected by changes. |
| **`@hyperflash-patch-executor`** | **Surgical Implementer** | Implements code changes with strict typing, Chunked Long-Decode, and pre-mortems. |
| **`@hyperflash-test-adversary`** | **Verification Engine** | Runs compiler, static analysis, unit tests, and reproducer scripts (Tiers 1-6). |
| **`@hyperflash-reviewer`** | **Independent Reviewer** | Performs independent static code review and diff auditing (Tier 8). |

---

## 📊 Verification Hierarchy (9 Tiers)

HyperFlash orders evidence rigor from strongest deterministic validation down to heuristic review:

1. **Tier 1:** Hidden deterministic acceptance validator
2. **Tier 2:** External integration / runtime execution
3. **Tier 3:** Project test suites (`pytest`, `jest`, `vitest`, `cargo test`, `go test`)
4. **Tier 4:** Compiler & static type checking (`py_compile`, `tsc --noEmit`, `mypy`)
5. **Tier 5:** Deterministic linters (`ruff`, `eslint`)
6. **Tier 6:** Executable reproducer scripts
7. **Tier 7:** Structural & diff invariants
8. **Tier 8:** Independent subagent review (`@hyperflash-reviewer`)
9. **Tier 9:** Same-model self-review (supplementary only; never completion evidence)

---

## 📁 Repository Structure

```
hyperflash/
├── .gitignore
├── LICENSE
├── README.md
├── install.sh
├── install.ps1
├── uninstall.sh
├── uninstall.ps1
└── src/
    ├── AGENTS.md
    ├── hooks.json
    ├── agents/
    │   ├── hyperflash.md
    │   ├── hyperflash-impact-auditor.md
    │   ├── hyperflash-investigator.md
    │   ├── hyperflash-patch-executor.md
    │   ├── hyperflash-reviewer.md
    │   └── hyperflash-test-adversary.md
    ├── rules/
    │   └── hyperflash-protocol.md
    ├── scripts/
    │   ├── build_symbol_graph.py
    │   ├── enforce_completion_stop_hook.py
    │   ├── enforce_hyperflash_pre_hook.py
    │   └── mark_mutation_post_hook.py
    └── skills/
        └── hyperflash/
            ├── SKILL.md
            ├── references/
            │   └── verification-and-contracts.md
            └── scripts/
                ├── hyperflash_decide.py
                └── verify_hierarchy.py
```

---

## 💻 CLI & IDE Usage

### CLI (`agy`)
```bash
# Launch Antigravity session with HyperFlash orchestrator
agy --agent hyperflash

# Or invoke directly with a prompt
agy --agent hyperflash "Refactor the authentication middleware to use JWT tokens"
```

### Antigravity IDE
Mention `@hyperflash` in your chat or prompt to activate the orchestrator for any repository-changing task:
```text
@hyperflash Refactor the payments service and ensure all tests pass
```

---

## 📄 License

MIT © [Virat Ghatge](https://github.com/Virat-Ghatge)
