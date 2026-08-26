# Bug Management & Resolution Protocol

## Core Hard Constraints
- **Code modifications, edits, and bug fixes** are **EXCLUSIVELY PERMITTED when the user explicitly invokes `/fix_bug`**.
- Commands like `/bug`, `/fr`, `/list_bugs`, `/triage_bug`, `/bug_plan`, and `/bug_review` MUST ONLY inspect codebase files or record metadata into `.agents/bugs.json` / `.agents/bug_plan.md`—they MUST NEVER modify source code, edit implementation files, or attempt to resolve the reported issue.
- **Test Execution**: Running automated tests is EXCLUSIVELY PERMITTED during `/triage_bug` (for root-cause investigation), `/fix_bug` (for reproduction and fix verification), and `/bug_review` (for regression checks). Running tests during `/bug`, `/fr`, `/list_bugs`, or `/bug_plan` is STRICTLY PROHIBITED.

## Database & Fields Schema (`.agents/bugs.json`)
- Single unified sequential integer IDs (`1, 2, 3...`) shared across Bugs and FRs.
- `type`: `"Bug"` or `"FR"`
- `reporter`: Auto-detected from `git config user.name` or `$USER`
- `date_reported`, `date_triaged`, `date_resolved` (format: `YYYY-MM-DD`)
- `priority`: `"P0"`, `"P1"`, `"P2"`, `"P3"`
- `impact`: `"Critical"`, `"High"`, `"Medium"`, `"Low"`
- `risk`: `"Low"`, `"Medium"`, `"High"`
- `status`: `"Reported"`, `"Investigated"`, `"Fix Proposed"`, `"Fix Implemented"`, `"Fix Verified"`, `"Obsolete"`, `"Reopened"`
- `phase`: `"Phase 1"`, `"Phase 2"`, `"Phase 3"`, `"Phase 4"`
