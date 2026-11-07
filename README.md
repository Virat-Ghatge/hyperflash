# ⚡ HyperFlash

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Runtime](https://img.shields.io/badge/Runtime-Python_3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Google_Antigravity-4285F4.svg)](https://antigravity.google/)
[![Engine](https://img.shields.io/badge/Engine-Gemini_3.8_Flash-8E75C2.svg)](https://deepmind.google/technologies/gemini/)

> **Autonomous multi-agent reliability runtime for Google Antigravity.** Engineered to force **Gemini 3.8 Flash** to deliver top-tier, enterprise-grade engineering output without context drift, lazy code elision, or broken builds.

---

## 🎯 Why HyperFlash?

Fast execution models (like Gemini 3.8 Flash) are lightning-quick and cost-effective, but they suffer from predictable failure modes on complex software engineering tasks:

* **Lazy Code Elision:** Under output pressure, fast models truncate code blocks with `// ... rest of implementation` or empty `pass` blocks.
* **Ungrounded Edits:** Modifying source files before reading callers or upstream type definitions, introducing cascading regressions.
* **Premature Victory:** Declaring *"I have fixed the issue!"* without compiling the code, running linters, or verifying test suites.
* **Native `/boost` Inefficiencies:** Antigravity's standard `/boost` command spins up heavy, full-agent swarms even for 2-line fixes, burning tokens and adding unnecessary latency.

**HyperFlash solves this by trading model parameter scale for structural scaffolding, AST indexing, and deterministic OS-level verification gates.**

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
(1) PreToolUse hook hard-blocks any replacement payload matching elision regexes.
(2) SessionStart hook generates a compact workspace symbol graph (.agents/state/symbol_graph.json).
(3) Stop hook denies task exit if files were mutated without a subsequent passing test run.
(4) Tool call hashes are recorded; identical retries of failed attempts are rejected immediately.
(5) Direct-mode triage routes single-file edits instantly without spawning redundant subagents.
```

---

## 🏛 Multi-Agent Architecture

HyperFlash enforces strict **tool-permission asymmetry**. The primary orchestrator is stripped of file-writing tools, making it impossible to bypass the verification loop or mutate code without a contract:

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

### The Subagent Team

| Subagent | Role | Permitted Tools | Core Responsibility |
|---|---|---|---|
| **`hyperflash`** | **Orchestrator** | Read, Search, Subagent Hooks | Evaluates task complexity, initializes `contract.json`, and coordinates subagents. Zero write tools. |
| **`hyperflash-investigator`** | **Reconnaissance** | `view_file`, `grep_search` | Inspects target files, identifies relevant tests, and localizes implementation areas. |
| **`hyperflash-impact-auditor`** | **Dependency Auditor** | `view_file`, `symbol_graph` | Traces callers across the repository to lock `allowed_write_scope` before any code changes. |
| **`hyperflash-patch-executor`** | **Implementation** | `replace_file_content` | Applies minimal, surgical diffs. Enforces Chunked Long-Decode and exhaustive static typing. |
| **`hyperflash-reviewer`** | **Code Reviewer** | `view_file`, `run_command` | Audits `git diff` against structural invariants and project conventions (Tier 8 Verification). |
| **`hyperflash-test-adversary`** | **Verification & QA** | `run_command` | Executes compilers, linters, and unit test suites (Tiers 1–6) to produce concrete pass/fail evidence. |

---

## 🛡 The 8 Watcher Invariants

Every action inside HyperFlash is governed by the 8 Watcher Invariants, enforced at the OS level via `~/.gemini/config/hooks.json`:

1. **Ground Before Mutating:** Target files must be viewed in the current session before edits are allowed.
2. **Stay in Declared Scope:** File edits outside `allowed_write_scope` in `contract.json` are rejected.
3. **Fresh Evidence Required:** The `Stop` hook blocks task completion unless tests pass *after* the latest file edit (`last_verified_ts >= last_mutation_ts`).
4. **Never Exact-Retry a Failure:** Failed tool inputs are fingerprinted via SHA-256 in `retry_ledger.json` to prevent identical retry loops.
5. **Satisfy the Contract:** Task completion is gated by explicit acceptance criteria.
6. **Report Reality Only:** Claims of passing builds or resolved bugs must cite actual terminal output.
7. **Zero Code Elision:** Regex hooks reject `// ... rest of code`, `# ... existing code`, or `TODO: implement` placeholders.
8. **Exhaustive Static Typing:** All parameters and return values must carry explicit static types; edits require counterfactual `<pre_mortem>` records.

---

## 🚀 Quick Install

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

The installer configures your global Antigravity environment (`~/.gemini/config/`) with all required agents, skills, rules, and lifecycle hooks.

---

## 💻 How to Use HyperFlash

HyperFlash integrates natively with both the Antigravity Desktop IDE and the CLI.

### 1. In the Antigravity Desktop IDE (Recommended)
You can invoke HyperFlash directly in your active conversation using any of these methods:
* **In-Chat Mention (`@hyperflash`):** Type `@hyperflash` directly in the prompt box followed by your task. This immediately routes the prompt through the HyperFlash orchestrator:
  ```text
  @hyperflash Refactor the event bus in src/events.py to support backpressure and ensure all unit tests pass.
  ```
* **Agent Selector Dropdown:** Click the Agent dropdown above the prompt input and choose **`hyperflash`**.
* **Slash Switcher:** Send `/agent hyperflash` in chat to lock the session to HyperFlash.

### 2. In the Antigravity CLI (`agy`)
* **Launch directly:**
  ```bash
  agy --agent hyperflash
  ```
* **Launch with an interactive prompt:**
  ```bash
  agy --agent hyperflash -i "Fix failing pytest assertions in tests/test_engine.py"
  ```
* **Switch mid-session:** Type `/agent hyperflash` inside any active CLI session.

---

## 🧪 Verification & Telemetry

HyperFlash maintains a real-time state ledger inside your project's `.agents/state/` folder:

* **`.agents/state/symbol_graph.json`:** Pre-indexed AST map containing all classes, methods, and line numbers.
* **`.agents/state/contract.json`:** Active task contract tracking `allowed_write_scope`, criteria, and `last_verified_ts`.
* **`.agents/state/retry_ledger.json`:** SHA-256 failure fingerprints preventing identical loops.

To verify the test suite and contract independently at any point, run:
```bash
python3 ~/.gemini/config/skills/hyperflash/scripts/verify_hierarchy.py
```

---

## 📄 License

MIT © [Virat Ghatge](https://github.com/Virat-Ghatge)
