---
description: cleanup, test, and commit workflow
---

1. Clean up temporary files
   - Remove `*.log`, `test_output.txt`, `debug_output.txt`
   - Remove `artifacts/uploads/*` (if they are test artifacts)
   - Find any other files that should be cleaned up which might be left over from development
   
2. Run unit tests
   - Run `uv run pytest` to ensure all tests pass.
   - If tests fail, STOP and notify the user (or fix them if minor).

3. Prepare for Commit
   - Run `git status` to view changes.
   - Generate a concise, descriptive commit message based on the changes.
   - Propose the commit message and branch strategy (current branch vs new branch) to the user.
   - Make sure we are not checking in any temporary files or artifacts

4. Commit Changes
   - **WAIT** for user approval.
   - User must approve the commit message and branch.
   - If approved:
     - `git add .`
     - `git commit -m "message"`
     - `git push` if remote is configured.
     - if there is no remote configured, notify the user.

5. Update Documentation
   - Check if any changes affect the user experience or system behavior.
   - Update `README.md` or relevant documentation if necessary.
   - Add any outstanding questions or issues to the `TODO` section of the README.  
   - Add any low priority tasks to the `BACKLOG` section of the README.
   - Ensure `IMPLEMENTATION_PLAN.md` is up to date if a major feature was added.
   - If there are obvious next steps when we resume, create a `resume_tasks.md` with the next steps.
