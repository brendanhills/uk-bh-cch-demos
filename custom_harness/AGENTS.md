# Global Rules

- **Bug Reporting & Management Protocol**:
  * **`/bug` Command**: When the user runs `/bug` or reports a bug, do NOT try to fix it immediately. Record the description, date, and workspace context into `<workspace-root>/.agents/bugs.json` with empty `"priority"` and `"impact"` fields (`""`) and status `"Reported"`.
  * **Definitions**:
    - **`impact`**: Measures *how much of the system is affected* by the bug (technical scope and severity).
    - **`priority`**: Represents the *order in which we should work on them* (resolution scheduling).
  * **`/list_bugs` Command**: Read `<workspace-root>/.agents/bugs.json` from the active workspace and render a clear, structured markdown table displaying all recorded bugs, their separate priority, impact, and status.
  * **`/triage_bug` Command Protocol**:
    - **With Argument (`/triage_bug #1`)**: Look up the specified bug ID inside `<workspace-root>/.agents/bugs.json`. Investigate the cause, formulate a solution plan, and assess the bug's `priority` (e.g., `"P0"`, `"P1"`, `"P2"`, `"P3"`) and `impact` (e.g., `"Critical"`, `"High"`, `"Medium"`, `"Low"`). Document the cause, proposed plan, priority, and impact into `.agents/bugs.json`, updating its status to `"Investigated"` or `"Fix Proposed"`. Do NOT execute the fix.
    - **Without Argument (`/triage_bug`)**: Read `<workspace-root>/.agents/bugs.json` and identify all bugs that have not yet been triaged (where `priority` and `impact` are empty `""`). Triage each untriaged bug by investigating cause, solution plan, priority, and impact, and update database records without executing fixes.
  * **`/fix_bug` Command Protocol**:
    - **With Argument (`/fix_bug #1`)**: Look up the bug ID inside `.agents/bugs.json`. Formulate a clear design plan. The **first task in implementing the fix must be to develop an automated reproduction unit test** that fails specifically due to this bug. Verify only that targeted test fails, then write code modifications required to resolve the bug. Verify that the reproduction unit test (and existing tests) pass successfully, and update status to `"Fix Implemented"`.
    - **Without Argument (`/fix_bug`)**: Read `.agents/bugs.json`, identify all remaining open/unverified bugs (status not `"Fix Verified"`), sort chronologically by priority (`P0` -> `P1` -> `P2` -> `P3`), and present a recommended sequence of resolution.

- **checkpoint**: When requested with "checkpoint" (or when you say "checkpoint" or "Finish for the day" or "finish for the day"), update the README.md and Resume.md (compaction summary), track status, check for any untracked project source files/directories in the active workspace (confirming .gitignore is clean), stage and commit all relevant modified and untracked project files with a descriptive message, and push the branch to the remote repository to ensure complete machine portability.

- **Python Package Management & Execution (`uv`)**: Always use `uv` commands (`uv sync`, `uv run`, `uv add`, `uv pip install`) for all Python package management, virtual environment creation, and script execution across all projects. Do not use standard `pip`, `python -m venv`, or direct binary invocation when `uv` is available.
