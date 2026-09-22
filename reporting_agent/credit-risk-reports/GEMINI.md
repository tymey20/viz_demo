# GEMINI.md
Follow AGENTS.md and STYLE.md in this repo; they apply to every task.

Antigravity-specific:
- Show a plan artifact listing files you will touch before editing.
- Run `pytest` and `reportkit build` for the affected report before reporting done, and
  include the validation output in your summary.
- Require explicit approval before any command that sets `REPORTKIT_BACKEND=bigquery`.
