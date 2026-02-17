---
description: fast-track mode for bug fixes and small iterations
---

1. **Identify**: pinpoint the issue or error message.
2. **Reproduce**: Create a reproduction script or test case that fails.
   - If a test already exists, run it to confirm failure.
3. **Fix**: Implement the fix in the codebase.
4. **Verify**: Run the reproduction script or test case again to confirm it passes.
   - Ensure no regressions.
   - If the fix is substantial, consider creating a new test case to cover the fix
  - if the fix is very large and complex, ask the user if they want to change to PLAN mode
5. **Finish**: Update `task.md` if applicable and ready for next task.

