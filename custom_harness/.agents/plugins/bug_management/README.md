# Bug Management Plugin (`bug_management`)

A comprehensive, production-grade bug and feature request tracking, triage, planning, review, and resolution plugin suite for Antigravity, Jetski, and Gemini CLI.

## 📦 Included Skills

| Skill | Slash Command | Description |
| :--- | :--- | :--- |
| **bug** | `/bug` | Record a bug report in `.agents/bugs.json` without fixing it immediately. |
| **fr** | `/fr` | Record a feature request in `.agents/bugs.json`. |
| **list_bugs** | `/list_bugs` | Render a structured markdown table of all bugs and feature requests. |
| **triage_bug** | `/triage_bug` | Investigate cause, plan solution, and assign priority/impact/risk. |
| **bug_plan** | `/bug_plan` | Generate phased implementation roadmap (`.agents/bug_plan.md`). |
| **bug_review** | `/bug_review` | Audit active and closed bugs for obsolescence or regressions. |
| **fix_bug** | `/fix_bug` | Develop automated reproduction test, implement fix, and verify resolution. |

## 🛡️ Rules & Constraints
- Code modifications are strictly restricted to the `/fix_bug` command.
- Test execution is restricted to `/triage_bug`, `/bug_review`, and `/fix_bug`.
- Single unified integer ID sequence (`1`, `2`, `3`...) across both bugs and feature requests.
