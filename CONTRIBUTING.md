# Contributing to HyperFlash ⚡

First off, thank you for considering contributing to **HyperFlash**! It is contributions like yours that make HyperFlash an open, robust, and reliable engineering runtime for Google Antigravity and the broader autonomous agent community.

---

## 📜 Table of Contents
1. [Code of Conduct](#-code-of-conduct)
2. [How Can I Contribute?](#-how-can-i-contribute)
   - [Reporting Bugs](#reporting-bugs)
   - [Suggesting Enhancements](#suggesting-enhancements)
   - [Contributing Code](#contributing-code)
3. [HyperFlash Core Invariants & Engineering Standards](#-hyperflash-core-invariants--engineering-standards)
4. [Local Development Setup](#-local-development-setup)
5. [Verification & Testing](#-verification--testing)
6. [Commit Message Guidelines](#-commit-message-guidelines)
7. [Pull Request Process](#-pull-request-process)
8. [Questions or Need Help?](#-questions-or-need-help)

---

## 🤝 Code of Conduct

This project and everyone participating in it is governed by the [HyperFlash Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to **viratghatge71@gmail.com**.

---

## 💡 How Can I Contribute?

### Reporting Bugs
Before creating a bug report, please check existing [Issues](https://github.com/Virat-Ghatge/hyperflash/issues) to ensure the issue has not already been reported.

When filing a bug, please use the **Bug Report** template and include:
* Operating System and version
* Antigravity CLI / Desktop IDE version
* Python version (`python3 --version`)
* A clear, minimal reproduction scenario
* Relevant log output from `.agents/state/contract.json` or hook logs

### Suggesting Enhancements
Feature suggestions are always welcome! When opening a **Feature Request**, explain:
* The problem you are trying to solve
* The proposed architecture or hook modification
* How the change interacts with the **8 Watcher Invariants**

### Contributing Code
Whether you are fixing a bug, adding AST parsing support for another language, or enhancing lifecycle hooks, follow the workflow outlined below.

---

## 🛡 HyperFlash Core Invariants & Engineering Standards

All contributions to HyperFlash must strictly uphold our core engineering principles:

1. **Zero Code Elision:** PRs must never introduce placeholder comments like `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Every code modification must be 100% complete and immediately executable.
2. **Exhaustive Static Typing:** All Python functions, arguments, and return values must include complete static type annotations. Untyped definitions will be rejected by our linting tier.
3. **Tool-Permission Asymmetry:** The `hyperflash` router orchestrator must remain purely non-destructive and read-only (zero file-editing tools). All mutations belong strictly in specialized subagents (such as `hyperflash-patch-executor`).
4. **Deterministic Lifecycle Hooks:** Hooks must be fast, portable across POSIX and Windows, and non-destructive to existing configurations in `~/.gemini/config/hooks.json`.

---

## 🛠 Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/Virat-Ghatge/hyperflash.git
cd hyperflash
```

### 2. Set up a Python Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install ruff pytest mypy
```

### 3. Test Installation Locally
You can test the non-destructive installation scripts in a staging or local directory:

**Linux / macOS:**
```bash
./install.sh
```

**Windows (PowerShell):**
```powershell
.\install.ps1
```

*Note: The installer automatically detects your home directory and configures `~/.gemini/config/` without overwriting third-party hooks.*

---

## 🧪 Verification & Testing

HyperFlash uses a 9-tier hierarchical verification framework. Before pushing code or submitting a pull request, run the static analysis and verification suite:

```bash
python3 src/skills/hyperflash/scripts/verify_hierarchy.py
```

Ensure the output ends with:
```text
VERDICT: PASS
```

If any tier fails (such as syntax error, type violation, or ruff formatting error), fix the reported issues and re-run until the verdict is `PASS`.

---

## 📝 Commit Message Guidelines

We enforce the [Conventional Commits](https://www.conventionalcommits.org/) specification:

* `feat:` A new feature or capability
* `fix:` A bug fix
* `docs:` Documentation updates only
* `style:` Formatting changes that do not affect code logic
* `refactor:` Code changes that neither fix a bug nor add a feature
* `test:` Adding or updating tests
* `chore:` Maintenance tasks, dependency updates, or build configs

**Example:**
```bash
git commit -m "feat: implement AST call-graph indexing for Rust source files"
```

---

## 🚀 Pull Request Process

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   ```
2. Make your surgical edits adhering to the **HyperFlash Invariants**.
3. Run verification tests to confirm `VERDICT: PASS`.
4. Ensure your branch is rebased on the latest `main`:
   ```bash
   git fetch origin
   git rebase origin/main
   ```
5. Push to your fork and submit a Pull Request using the [PR Template](.github/PULL_REQUEST_TEMPLATE.md).
6. Address review comments promptly. Once CI and reviewers sign off, your PR will be merged!

---

## 💬 Questions or Need Help?

* Open a discussion in [GitHub Issues](https://github.com/Virat-Ghatge/hyperflash/issues).
* Contact the maintainer: **Virat Ghatge** ([viratghatge71@gmail.com](mailto:viratghatge71@gmail.com)).

Thank you for helping make HyperFlash the most reliable agentic runtime in the ecosystem! ⚡