#!/usr/bin/env python3
"""
Scaffolds the complete GitHub repository for HyperFlash at ~/hyperflash and the active workspace.
Copies active configuration files from ~/.gemini/config/, writes README, LICENSE,
.gitignore, install/uninstall scripts, and initializes git on branch main.
"""
import os
import shutil
import stat
import subprocess
from pathlib import Path

HOME = Path.home()
REPO_ROOT = HOME / "hyperflash"
CWD_REPO = Path.cwd()
SRC_DIR = REPO_ROOT / "src"
CFG_GLOBAL = HOME / ".gemini" / "config"

print("=== Scaffolding HyperFlash GitHub Repository ===")
print(f"Target Repository: {REPO_ROOT}")
print(f"Source Config:     {CFG_GLOBAL}")

# 1. Create directory structure
dirs_to_create = [
    SRC_DIR / "agents",
    SRC_DIR / "rules",
    SRC_DIR / "scripts",
    SRC_DIR / "skills" / "hyperflash" / "references",
    SRC_DIR / "skills" / "hyperflash" / "scripts",
]
for d in dirs_to_create:
    d.mkdir(parents=True, exist_ok=True)

# 2. Copy installed files from ~/.gemini/config/
files_to_copy = [
    (CFG_GLOBAL / "AGENTS.md", SRC_DIR / "AGENTS.md"),
    (CFG_GLOBAL / "hooks.json", SRC_DIR / "hooks.json"),
    (CFG_GLOBAL / "rules" / "hyperflash-protocol.md", SRC_DIR / "rules" / "hyperflash-protocol.md"),
    (CFG_GLOBAL / "skills" / "hyperflash" / "SKILL.md", SRC_DIR / "skills" / "hyperflash" / "SKILL.md"),
    (CFG_GLOBAL / "skills" / "hyperflash" / "references" / "verification-and-contracts.md", SRC_DIR / "skills" / "hyperflash" / "references" / "verification-and-contracts.md"),
    (CFG_GLOBAL / "skills" / "hyperflash" / "scripts" / "hyperflash_decide.py", SRC_DIR / "skills" / "hyperflash" / "scripts" / "hyperflash_decide.py"),
    (CFG_GLOBAL / "skills" / "hyperflash" / "scripts" / "verify_hierarchy.py", SRC_DIR / "skills" / "hyperflash" / "scripts" / "verify_hierarchy.py"),
    (CFG_GLOBAL / "scripts" / "build_symbol_graph.py", SRC_DIR / "scripts" / "build_symbol_graph.py"),
    (CFG_GLOBAL / "scripts" / "enforce_hyperflash_pre_hook.py", SRC_DIR / "scripts" / "enforce_hyperflash_pre_hook.py"),
    (CFG_GLOBAL / "scripts" / "mark_mutation_post_hook.py", SRC_DIR / "scripts" / "mark_mutation_post_hook.py"),
    (CFG_GLOBAL / "scripts" / "enforce_completion_stop_hook.py", SRC_DIR / "scripts" / "enforce_completion_stop_hook.py"),
]

for src, dst in files_to_copy:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"Copied {src.name} -> {dst.relative_to(REPO_ROOT)}")
    else:
        print(f"WARNING: File not found {src}")

# Copy all flat agent files
agent_count = 0
for agent_file in (CFG_GLOBAL / "agents").glob("hyperflash*.md"):
    dst = SRC_DIR / "agents" / agent_file.name
    shutil.copy2(agent_file, dst)
    agent_count += 1
    print(f"Copied agent: {agent_file.name}")
print(f"Total agents copied: {agent_count}")

# 3. Create install.sh
INSTALL_SH = r"""#!/usr/bin/env bash
set -e

DEST="$HOME/.gemini/config"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing HyperFlash to $DEST ==="
mkdir -p "$DEST"/{agents,skills/hyperflash/references,skills/hyperflash/scripts,rules,scripts}

cp "$REPO_DIR/src/AGENTS.md" "$DEST/AGENTS.md"
cp "$REPO_DIR/src/hooks.json" "$DEST/hooks.json"
cp "$REPO_DIR/src/rules/hyperflash-protocol.md" "$DEST/rules/"
cp "$REPO_DIR/src/agents/"*.md "$DEST/agents/"
cp "$REPO_DIR/src/skills/hyperflash/SKILL.md" "$DEST/skills/hyperflash/"
cp "$REPO_DIR/src/skills/hyperflash/references/"* "$DEST/skills/hyperflash/references/"
cp "$REPO_DIR/src/skills/hyperflash/scripts/"*.py "$DEST/skills/hyperflash/scripts/"
cp "$REPO_DIR/src/scripts/"*.py "$DEST/scripts/"

# Adjust hooks.json paths to match local installation directory
sed -i "s|C:/Users/[^/]*/\.gemini/config|$DEST|g" "$DEST/hooks.json" 2>/dev/null || sed -i '' "s|C:/Users/[^/]*/\.gemini/config|$DEST|g" "$DEST/hooks.json" 2>/dev/null || true

chmod +x "$DEST/scripts/"*.py "$DEST/skills/hyperflash/scripts/"*.py

echo "[OK] HyperFlash successfully installed!"
echo "Run 'agy --agent hyperflash' or mention '@hyperflash' in the Antigravity IDE."
"""
install_sh_path = REPO_ROOT / "install.sh"
install_sh_path.write_text(INSTALL_SH.strip() + "\n", encoding="utf-8")
install_sh_path.chmod(install_sh_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

# 4. Create install.ps1
INSTALL_PS1 = r"""$DEST = Join-Path $HOME ".gemini\config"
$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

Write-Host "=== Installing HyperFlash to $DEST ===" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "$DEST\\agents", "$DEST\\skills\\hyperflash\\references", "$DEST\\skills\\hyperflash\\scripts", "$DEST\\rules", "$DEST\\scripts" | Out-Null

Copy-Item "$PSScriptRoot\\src\\AGENTS.md" "$DEST\\AGENTS.md" -Force
Copy-Item "$PSScriptRoot\\src\\hooks.json" "$DEST\\hooks.json" -Force
Copy-Item "$PSScriptRoot\\src\\rules\\hyperflash-protocol.md" "$DEST\\rules\\" -Force
Copy-Item "$PSScriptRoot\\src\\agents\\*.md" "$DEST\\agents\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\SKILL.md" "$DEST\\skills\\hyperflash\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\references\\*" "$DEST\\skills\\hyperflash\\references\\" -Force
Copy-Item "$PSScriptRoot\\src\\skills\\hyperflash\\scripts\\*.py" "$DEST\\skills\\hyperflash\\scripts\\" -Force
Copy-Item "$PSScriptRoot\\src\\scripts\\*.py" "$DEST\\scripts\\" -Force

# Normalize hook paths in hooks.json
$destNormalized = $DEST -replace '\\\\', '/'
$hooksFile = "$DEST\\hooks.json"
if (Test-Path $hooksFile) {
    $content = Get-Content $hooksFile -Raw
    $content = $content -replace 'C:/Users/[^/]+/\.gemini/config', $destNormalized
    Set-Content $hooksFile -Value $content -NoNewline
}

Write-Host "[OK] HyperFlash successfully installed!" -ForegroundColor Green
Write-Host "Run 'agy --agent hyperflash' or mention '@hyperflash' in the Antigravity IDE."
"""
(REPO_ROOT / "install.ps1").write_text(INSTALL_PS1.strip() + "\n", encoding="utf-8")

# 5. Create uninstall.sh and uninstall.ps1
UNINSTALL_SH = """#!/usr/bin/env bash
set -e

DEST="$HOME/.gemini/config"
echo "=== Uninstalling HyperFlash from $DEST ==="

rm -f "$DEST/agents/hyperflash"*.md
rm -rf "$DEST/skills/hyperflash"
rm -f "$DEST/rules/hyperflash-protocol.md"
rm -f "$DEST/scripts/build_symbol_graph.py"
rm -f "$DEST/scripts/enforce_hyperflash_pre_hook.py"
rm -f "$DEST/scripts/mark_mutation_post_hook.py"
rm -f "$DEST/scripts/enforce_completion_stop_hook.py"

echo "[OK] HyperFlash removed. Note: $DEST/hooks.json was retained to protect other tools."
"""
uninstall_sh_path = REPO_ROOT / "uninstall.sh"
uninstall_sh_path.write_text(UNINSTALL_SH.strip() + "\n", encoding="utf-8")
uninstall_sh_path.chmod(uninstall_sh_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

UNINSTALL_PS1 = """$DEST = Join-Path $HOME ".gemini\\config"
Write-Host "=== Uninstalling HyperFlash from $DEST ===" -ForegroundColor Yellow

Remove-Item "$DEST\\agents\\hyperflash*.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\skills\\hyperflash" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\rules\\hyperflash-protocol.md" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\scripts\\build_symbol_graph.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\scripts\\enforce_hyperflash_pre_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\scripts\\mark_mutation_post_hook.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$DEST\\scripts\\enforce_completion_stop_hook.py" -Force -ErrorAction SilentlyContinue

Write-Host "[OK] HyperFlash removed. Note: $DEST\\hooks.json was retained to protect other tools." -ForegroundColor Green
"""
(REPO_ROOT / "uninstall.ps1").write_text(UNINSTALL_PS1.strip() + "\n", encoding="utf-8")

# 6. Create .gitignore
GITIGNORE = """.DS_Store
__pycache__/
*.py[cod]
*$py.class
*.log
.agents/state/
.venv/
env/
dist/
build/
"""
(REPO_ROOT / ".gitignore").write_text(GITIGNORE.strip() + "\n", encoding="utf-8")

# 7. Create LICENSE
LICENSE = """MIT License

Copyright (c) 2026 Virat Ghatge

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
(REPO_ROOT / "LICENSE").write_text(LICENSE.strip() + "\n", encoding="utf-8")

# 8. Create README.md
README = """# ⚡ HyperFlash

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
git clone https://github.com/Virat-Ghatge/hyperflash.git "$HOME\\hyperflash"
cd "$HOME\\hyperflash"
.\\install.ps1
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
"""
(REPO_ROOT / "README.md").write_text(README.strip() + "\n", encoding="utf-8")

# 9. Copy to current working directory if different from REPO_ROOT
if CWD_REPO.resolve() != REPO_ROOT.resolve():
    print(f"\nMirroring staged repository files to active workspace: {CWD_REPO}")
    for item in REPO_ROOT.iterdir():
        if item.name == ".git":
            continue
        dest_item = CWD_REPO / item.name
        if item.is_dir():
            shutil.copytree(item, dest_item, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest_item)
    print("[OK] Workspace mirrored successfully.")

# 10. Initialize git repository at REPO_ROOT
print(f"\n=== Initializing Git Repository at {REPO_ROOT} ===")

def run_git(args, cwd):
    res = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"git {' '.join(args)} stderr: {res.stderr.strip()}")
    return res

# Check git user name / email
subprocess.run(["git", "config", "user.name"], capture_output=True)
run_git(["init"], cwd=REPO_ROOT)
run_git(["branch", "-M", "main"], cwd=REPO_ROOT)
run_git(["add", "."], cwd=REPO_ROOT)
commit_res = run_git(["commit", "-m", "feat: initial release of HyperFlash reliability runtime for Google Antigravity"], cwd=REPO_ROOT)
print(commit_res.stdout.strip())

# Initialize git at CWD_REPO if not already a git repository
if CWD_REPO.resolve() != REPO_ROOT.resolve():
    run_git(["init"], cwd=CWD_REPO)
    run_git(["branch", "-M", "main"], cwd=CWD_REPO)
    run_git(["add", "."], cwd=CWD_REPO)
    cwd_commit = run_git(["commit", "-m", "feat: initial release of HyperFlash reliability runtime for Google Antigravity"], cwd=CWD_REPO)
    if cwd_commit.returncode == 0:
        print("Initialized and committed active workspace repo on main.")

# 11. Print final git status and directory tree
print("\n" + "="*50)
print("GIT STATUS (at ~/hyperflash):")
print("="*50)
status_res = subprocess.run(["git", "status"], cwd=REPO_ROOT, capture_output=True, text=True)
print(status_res.stdout)

print("="*50)
print("GIT LOG (at ~/hyperflash):")
print("="*50)
log_res = subprocess.run(["git", "log", "-n", "1", "--oneline"], cwd=REPO_ROOT, capture_output=True, text=True)
print(log_res.stdout)

print("="*50)
print("DIRECTORY TREE (at ~/hyperflash):")
print("="*50)
for root, dirs, files in os.walk(REPO_ROOT):
    if ".git" in root:
        continue
    rel_root = Path(root).relative_to(REPO_ROOT)
    indent = "    " * len(rel_root.parts)
    folder_name = rel_root.name if rel_root.parts else REPO_ROOT.name
    print(f"{indent}📂 {folder_name}/")
    for f in sorted(files):
        print(f"{indent}    📄 {f}")

print("\n[SUCCESS] HyperFlash production repository successfully staged and sealed!")
