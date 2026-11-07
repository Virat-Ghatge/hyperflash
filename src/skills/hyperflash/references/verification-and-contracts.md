# HyperFlash Contract Schema & Verification Escalation Reference

## `.agents/state/contract.json` Schema
- `mode`: `implement` | `debug` | `plan` | `review` | `security-review` | `migration`
- `effort_profile`: `eco` | `balanced` | `deep`
- `planning`: `direct` | `compact` | `deep` | `replan`
- `allowed_write_scope`: Array of permitted file paths or directory prefixes.
- `acceptance_criteria`: Array of verifiable requirements.
