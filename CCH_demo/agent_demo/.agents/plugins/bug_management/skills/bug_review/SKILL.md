---
name: bug_review
description: Audit active and recently closed bugs against current codebase state, git history, and targeted unit tests to detect obsolete bugs or regressions.
---

# Bug Review Command (`/bug_review`)

When the user runs `/bug_review`:

1. **Scope Selection**:
   - **Default (`/bug_review`)**: Audits all active/open bugs (to check if architectural changes rendered them obsolete) AND recently closed/resolved bugs (to check if recent changes caused regressions requiring re-opening).
   - **Targeted (`/bug_review #id`)**: Audits a single specified bug ID.
   - **Full Archive (`/bug_review all`)**: Audits all historical bugs in `.agents/bugs.json`.

2. **Audit & Evidence Gathering Protocol**:
   - **Codebase & Git Inspection**: Check git commit history (`git log`, `git diff`) for recent updates affecting the bug's context. Inspect whether referenced files, functions, or UI components still exist or have been refactored/removed.
   - **Targeted Unit Testing**: If targeted reproduction unit tests exist for a candidate bug, execute ONLY those specific tests (avoid full regression test runs) to verify current behavior.

3. **Status Assessment**:
   - **Active Bug -> Obsolete**: If architectural or codebase changes removed the affected feature/component or eliminated the root cause, update status to `"Obsolete"`.
   - **Closed Bug -> Reopened**: If recent commits broke a previously fixed bug or if targeted tests fail, update status to `"Reopened"`.
   - **Active Bug -> Fix Verified**: If targeted tests now pass or code changes resolved the issue completely, update status to `"Fix Verified"`.

4. **Database & Record Updates**:
   - Update `<workspace-root>/.agents/bugs.json` with new status and record rationale in a `"review_notes"` field (with timestamp and review reason).

5. **Summary Reporting**:
   - Render a structured markdown table in the conversation summarizing reviewed bugs, status changes, and review rationale.
