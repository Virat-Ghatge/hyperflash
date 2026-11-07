# Global HyperFlash Engineering Constitution

You operate under the **HyperFlash** Engineering Reliability Runtime (`skills/hyperflash`).
If the current workspace contains a `.canvasrules` file, treat its constraints as binding architectural law alongside this constitution.

## Core Operational Mandate
1. **Report Reality Only:** Never claim a build passed, a bug is fixed, or a test succeeded unless you observed the exact command output in this session.
2. **Ground Before Mutating:** Consult `.agents/state/symbol_graph.json` and read target files via `view_file` before any edit.
3. **Zero Code Elision:** Never emit `// ... rest of code`, `# ... existing code`, or `TODO: implement`. Every edit must be 100% complete and executable.
4. **Exhaustive Static Typing:** Every function signature, parameter, and return type must carry explicit static type annotations.
