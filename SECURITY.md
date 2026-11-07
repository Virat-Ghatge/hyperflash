# Security Policy 🛡️

HyperFlash is engineered to provide deterministic reliability and safety guarantees for autonomous coding agents. We treat security, sandboxing, and execution integrity with paramount priority.

---

## 🔒 Supported Versions

We provide active security patches and updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, security bypass in our invariant enforcement hooks, or unauthorized tool-execution vectors within HyperFlash, please disclose it responsibly.

**Please do NOT report security vulnerabilities via public GitHub issues.**

Instead, please report security concerns directly to the maintainer:
* **Security Contact:** Virat Ghatge
* **Email:** [viratghatge71@gmail.com](mailto:viratghatge71@gmail.com)
* **Subject Line:** `[SECURITY] Vulnerability in HyperFlash: <Brief Description>`

### What to Include in Your Report
To help us triage and resolve the issue quickly, please provide:
1. A clear description of the vulnerability (e.g., hook circumvention, unexpected command execution, AST parsing flaw).
2. Steps to reproduce the vulnerability, including sample prompts, configurations, or repository state.
3. Proof-of-concept payload or log output.
4. Any potential impact or attack vector you have identified.

### Response Timeline
* **Initial Acknowledgement:** Within 24-48 hours.
* **Triage & Status Update:** Within 5 business days with an assessment of severity.
* **Patch Release & Advisory:** A patch will be tested, verified through our 9-tier verification hierarchy, and published with an attribution advisory.

---

## 🏛 HyperFlash Security Architecture

HyperFlash implements a defense-in-depth model for coding agent security:

1. **Tool-Permission Asymmetry:** The primary `hyperflash` orchestrator possesses zero write tools (`replace_file_content`, `write_to_file`). It is mathematically impossible for the orchestrator to mutate code without delegating to a scoped subagent.
2. **Deterministic OS Lifecycle Hooks:**
   - **`PreToolUse`:** Rejects edits outside declared scope and blocks any elided code payloads.
   - **`PostToolUse`:** Tracks exact modification timestamps and hashes failed tool calls in an append-only ledger (`retry_ledger.json`).
   - **`Stop`:** Gates session termination until fresh verification passes.
3. **Local & Sandboxed Execution:** HyperFlash operates purely on your local machine within your Antigravity environment (`~/.gemini/config/`). It never transmits your source code, AST graphs, or tokens to third-party endpoints.