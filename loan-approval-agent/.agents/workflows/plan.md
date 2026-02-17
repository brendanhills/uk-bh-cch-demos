---
description: comprehensive planning mode for new features or major changes
---

1. **Initialize Task**: Create or update `task.md` with the new high-level objective.
2. **Research**: Analyze the codebase, dependencies, and requirements.
3. **Draft Plan**: Create or update `IMPLEMENTATION_PLAN.md`.
   - Define the Goal.
   - List Proposed Changes (File-by-file).
   - Define Verification Plan (Tests/Manual).
4. **Review**: Call `notify_user` to request review of `IMPLEMENTATION_PLAN.md`.
   - Set `BlockedOnUser=True`.
   - Explicitly ask for approval before proceeding.
   - The user must say "yes" to proceed.
   - Do NOT proceed until approved.
   - **CRITICAL**: Check for **Breaking Changes**.
   - If the change breaks existing APIs, data structures, or tests in a way that requires significant refactoring or affects other components, **ALERT THE USER**.
   - Suggest creating a feature branch or getting explicit approval for the breaking change.
