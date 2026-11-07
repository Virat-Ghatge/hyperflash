---
name: Bug Report
about: Report a bug, unexpected behavior, or invariant bypass in HyperFlash
title: '[BUG] '
labels: ['bug', 'triage']
assignees: ''
---

### 🐛 Bug Description
A clear and concise description of what the bug is.

### 🔄 Steps to Reproduce
1. In Antigravity IDE chat or terminal CLI, run: `...`
2. Submit prompt: `...`
3. Observe tool calls or subagent execution: `...`

### 🔍 Expected Behavior
A clear and concise description of what you expected to happen according to HyperFlash invariants.

### 📸 Observed Behavior & Error Output
```text
Paste terminal output, error logs, or hook rejection messages here
```

### 💻 Environment Information
* **OS:** (e.g., Ubuntu 22.04 / macOS Sonoma 14.5 / Windows 11)
* **Antigravity Interface:** (Antigravity Desktop IDE / `agy` CLI)
* **Underlying Engine:** (Gemini 3.8 Flash / Gemini 3.8 Pro / other)
* **Python Version:** (`python3 --version`)
* **HyperFlash Version / Commit:** (`git rev-parse --short HEAD`)

### 📋 Diagnostic Context (`.agents/state/`)
* [ ] Content of `.agents/state/contract.json` (if applicable)
* [ ] Content of `~/.gemini/config/hooks.json`

### 💡 Additional Context
Add any other context, edge cases, or screenshots about the problem here.