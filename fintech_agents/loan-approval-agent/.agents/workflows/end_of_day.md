---
description: cleanup, test, and commit workflow
---

1. Clean up temporary files
   - Remove `*.log`, `test_output.txt`, `debug_output.txt`
   - Remove `artifacts/uploads/*` (if they are test artifacts)
   
2. Run unit tests
   - Run `uv run pytest` to ensure all tests pass.
   - If tests fail, STOP and notify the user (or fix them if minor).

3. Prepare for Commit
   - Run `git status` to view changes.
   - Generate a concise, descriptive commit message based on the changes.
   - Propose the commit message and branch strategy (current branch vs new branch) to the user.

4. Commit Changes
   - **WAIT** for user approval.
   - User must approve the commit message and branch.
   - If approved:
     - `git add .`
     - `git commit -m "message"`
     - (Optional) `git push` if remote is configured.
