## ⚡ HyperFlash Pull Request

### 📝 Description of Changes
Briefly summarize the changes introduced in this PR and why they are necessary.

### 🔗 Related Issues
Fixes #(issue number) or Addresses #(issue number)

---

### 🛡 HyperFlash Invariant Compliance Checklist
Please verify that your pull request adheres to all HyperFlash reliability standards:

- [ ] **Zero Code Elision:** No `// ... rest of code`, `# ... existing code`, or `TODO` placeholders exist in any modified file.
- [ ] **Exhaustive Static Typing:** All modified or newly created functions/methods include complete type annotations.
- [ ] **Deterministic Scoping:** All edits are strictly bounded to the target scope.
- [ ] **Non-Destructive Hooks:** Any changes to `install.sh`, `install.ps1`, or `hooks.json` preserve third-party hook configurations.
- [ ] **Verification Hierarchy Passing:** Ran `verify_hierarchy.py` and obtained `VERDICT: PASS`.
- [ ] **Documentation Updated:** `README.md`, `AGENTS.md`, or `SKILL.md` updated if interfaces or invariant behaviors were modified.

---

### 🧪 Verification Evidence
Paste the output of your local verification test run below:

```text
[Paste verification command output showing VERDICT: PASS]
```