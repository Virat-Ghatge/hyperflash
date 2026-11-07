# ⚡ HyperFlash

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Google_Antigravity-4285F4.svg)](https://antigravity.google/)
[![Engine](https://img.shields.io/badge/Engine-Gemini_3.8_Flash-8E75C2.svg)](https://deepmind.google/technologies/gemini/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)

> **High-rigor multi-agent reliability runtime for Google Antigravity.** Engineered to force fast, low-cost engines like **Gemini 3.8 Flash** to deliver top-tier, enterprise-grade coding performance without context drift, lazy truncation comments, or broken builds.

---

## 💡 Why HyperFlash?

Fast execution models (like Gemini 3.8 Flash) are blazing fast and token-efficient, but they suffer from predictable structural failure modes on real-world engineering tasks:

* **Lazy Truncation Comments:** Under token pressure, models truncate large files with comments like `// ... rest of implementation` or empty `pass` blocks.
* **Ungrounded Mutations:** Editing functions before verifying upstream callers or static type signatures, breaking project builds.
* **Premature Victory:** Declaring *"I have fixed the bug!"* without executing the compiler, linter, or test suite.
* **Native `/boost` Inefficiencies:** Antigravity's default `/boost` command unconditionally spins up full subagent swarms even for 2-line fixes, burning tokens and causing high latency.

**HyperFlash trades parameter scale for deterministic structural scaffolding:** combining pre-computed AST call graphs, tool-permission asymmetry, and machine-enforced OS lifecycle hooks to guarantee production-grade code output.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 THE HYPERFLASH ADVANTAGE                               │
├──────────────────────────┬───────────────────┬───────────────────┬─────────────────────┤
│ Dimension                │ Vanilla 3.8 Flash │ Native /boost     │ HyperFlash ⚡       │
├──────────────────────────┼───────────────────┼───────────────────┼─────────────────────┤
│ Code Completeness        │ Frequent elision  │ Occasional elision│ 100% Guaranteed (1) │
│ Upstream Caller Tracking │ Unreliable        │ Broad grep scans  │ AST Symbol Graph (2)│
│ Premature Completion     │ Very High         │ Moderate          │ Blocked by Hook (3) │
│ Byte-Identical Loops     │ Common on failure │ Possible          │ SHA-256 Ledger (4)  │
│ Trivial Task Latency     │ 2–4s              │ 30–60s (Swarm)    │ Adaptive Triage (5) │
│ Cost & Quota Footprint   │ Minimal           │ High Token Burn   │ Highly Optimized    │
└──────────────────────────┴───────────────────┴───────────────────┴─────────────────────┘
(1) PreToolUse hook blocks any edit payload containing truncation or elision comments.
(2) SessionStart hook generates a compact workspace symbol index (.agents/state/symbol_graph.json).
(3) Stop hook denies task completion if files were modified without a subsequent passing test run.
(4) Tool call hashes are recorded in retry_ledger.json; identical retries of failed calls are rejected.
(5) Adaptive complexity routing executes 1-file edits instantly without spawning redundant subagents.
```

---

## 🚀 Quick Install

Run the installer from your terminal to configure HyperFlash globally in `~/.gemini/config/`.

### Linux & macOS
```bash
git clone https://github.com/Virat-Ghatge/hyperflash.git
cd hyperflash
./install.sh
```

### Windows (PowerShell)
```powershell
git clone https://github.com/Virat-Ghatge/hyperflash.git
cd hyperflash
.\install.ps1
```

*The installer is non-destructive: it merges HyperFlash hooks into your existing `hooks.json` without overwriting third-party configurations.*

---

## 💻 How to Use HyperFlash

HyperFlash integrates natively with both the **Antigravity Desktop IDE** and the **`agy` CLI**.

### 1. In the Antigravity Desktop IDE (Recommended)
You can invoke HyperFlash directly inside your conversation prompt box:

* **In-Chat Mention (`@hyperflash`):** Type `@hyperflash` directly in the prompt input followed by your request. Antigravity autocompletes the agent name and immediately routes the turn through the HyperFlash orchestrator:
  ```text
  @hyperflash Refactor src/pipeline.py to add bounded async backpressure and ensure all unit tests pass.
  ```
* **Agent Selector Dropdown:** Click the Agent dropdown above the chat input field and select **`hyperflash`**.
* **Slash Switcher:** Type `/agent hyperflash` in the chat to lock the session to HyperFlash.

### 2. In the Antigravity CLI (`agy`)
* **Launch directly:**
  ```bash
  agy --agent hyperflash
  ```
* **Launch with an initial prompt:**
  ```bash
  agy --agent hyperflash -i "Fix failing pytest assertions in tests/test_engine.py"
  ```
* **Switch mid-session:** Type `/agent hyperflash` inside any active CLI conversation.

---

## 🏛 Multi-Agent Architecture

HyperFlash enforces strict **tool-permission asymmetry**. The primary orchestrator is stripped of file-writing tools, making it impossible to bypass the verification loop or mutate code without a formal contract:

```
                          ┌───────────────────────────────┐
                          │     hyperflash (Router)       │
                          │(Read-Only + Subagent Invoker) │
                          └───────────────┬───────────────┘
                                          │
                  ┌───────────────────────┼───────────────────────┐
                  ▼                       ▼                       ▼
         ┌──────────────────┐    ┌───────────────────┐   ┌──────────────────┐
         │   investigator   │    │  patch-executor   │   │  test-adversary  │
         │(Read-Only Recon) │    │ (Surgical Diffs)  │   │(9-Tier Verifier) │
         └──────────────────┘    └───────────────────┘   └──────────────────┘
                  │                                               ▲
                  ▼                                               │
         ┌──────────────────┐                                     │
         │  impact-auditor  │                                     │
         │(Call-Graph Scope)│─────────────────────────────────────┘
```

| Agent Name | Role | Permitted Tools | Core Responsibility |
|---|---|---|---|
| **`hyperflash`** | **Orchestrator** | Read, Search, Subagent Hooks | Evaluates task complexity, initializes `contract.json`, and coordinates subagents. Zero write tools. |
| **`hyperflash-investigator`** | **Reconnaissance** | `view_file`, `grep_search` | Inspects target files, identifies relevant tests, and localizes implementation areas. |
| **`hyperflash-impact-auditor`** | **Dependency Auditor** | `view_file`, `symbol_graph` | Traces callers across the repository to lock `allowed_write_scope` before any code changes. |
| **`hyperflash-patch-executor`** | **Implementation** | `replace_file_content` | Applies minimal, surgical diffs. Enforces Chunked Long-Decode and exhaustive static typing. |
| **`hyperflash-reviewer`** | **Code Reviewer** | `view_file`, `run_command` | Audits `git diff` against structural invariants and project conventions (Tier 8 Verification). |
| **`hyperflash-test-adversary`** | **Verification & QA** | `run_command` | Executes compilers, linters, and unit test suites (Tiers 1–6) to produce concrete pass/fail evidence. |

---

## 🛡 The 8 Watcher Invariants

Every file edit and task completion is deterministically governed by OS-level hooks in `~/.gemini/config/hooks.json`:

1. **Ground Before Mutating:** Target files must be viewed via `view_file` in the current session before edits are permitted.
2. **Stay in Declared Scope:** Mutations outside `allowed_write_scope` in `contract.json` are rejected by the `PreToolUse` hook.
3. **Fresh Evidence Required:** The `Stop` hook blocks task completion unless tests pass *after* the latest file edit (`last_verified_ts >= last_mutation_ts`).
4. **Never Exact-Retry a Failure:** SHA-256 tool hashing in `retry_ledger.json` blocks byte-identical retries.
5. **Satisfy the Contract:** Completion is gated by explicit acceptance criteria recorded in `contract.json`.
6. **Report Reality Only:** Claims of passing builds or resolved bugs must cite actual observed terminal output.
7. **Zero Code Elision:** Pre-tool regex hooks reject `// ... rest of code`, `# ... existing code`, or `TODO: implement` placeholders.
8. **Exhaustive Static Typing:** All parameters and return values must carry explicit static types; edits require counterfactual `<pre_mortem>` records.

---

## 📁 Repository Structure

```text
hyperflash/
├── install.sh                              # Linux/macOS non-destructive installer
├── install.ps1                             # Windows PowerShell installer
├── uninstall.sh                            # Prunes HyperFlash from global config
├── LICENSE                                 # MIT License
├── README.md                               # Technical documentation
└── src/
    ├── AGENTS.md                           # Global system constitution
    ├── hooks.json                          # Portable lifecycle hooks template
    ├── rules/
    │   └── hyperflash-protocol.md          # Always-on protocol rule
    ├── agents/
    │   ├── hyperflash.md                   # Main Orchestrator
    │   ├── hyperflash-investigator.md      # Recon subagent
    │   ├── hyperflash-impact-auditor.md    # Caller impact subagent
    │   ├── hyperflash-patch-executor.md    # Implementation subagent
    │   ├── hyperflash-reviewer.md          # Review subagent
    │   └── hyperflash-test-adversary.md    # Verification subagent
    ├── skills/
    │   └── hyperflash/
    │       ├── SKILL.md                    # Core reliability runtime specification
    │       ├── references/                 # Schema & escalation guidelines
    │       └── scripts/                    # Decide CLI & 9-tier test verification
    └── scripts/
        ├── build_symbol_graph.py           # SessionStart AST indexer
        ├── enforce_hyperflash_pre_hook.py   # PreToolUse invariant guard
        ├── mark_mutation_post_hook.py      # PostToolUse timestamp & failure tracker
        └── enforce_completion_stop_hook.py # Stop gate verifier
```

---

## 📄 License
MIT © [Virat Ghatge](https://github.com/Virat-Ghatge)
