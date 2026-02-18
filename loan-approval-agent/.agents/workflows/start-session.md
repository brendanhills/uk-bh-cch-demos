---
description: run at the start of a session
---
- ONLY consider the current folder state when creating the plan.
- Review the following sources to understand the current project folder state:
  - TODO
  - BACKLOG
 
  - conversation history from last session
  - resume_tasks.md
  - IMPLEMENTATION_PLAN.md
  - git status
  - git log
  - git diff
  - unit test failures (don't run pytest, just read the failures)
  - integration test failures (don't run pytest, just read the failures)
  - end to end test failures (don't run pytest, just read the failures)

- Review previous session's 
  -TASKS
  - Walkthrough
  - Implementation Plan

- Go into planning mode

- Ask the user for their top priority for the day and incorporate it into the plan.
- Ask the user for any low priority or out of scope tasks they would like to add to the backlog.
- Ask the user for any other information they would like to share.
- Create a plan for the day and propose it to the user for approval.
- The user must explicitly approve the plan before the agent can proceed.



- Ask the user for their top priority for the day and incorporate it into the plan.
- Ask the user for any low priority or out of scope tasks they would like to add to the backlog.
- Ask the user for any other information they would like to share.
- Create a plan for the day and propose it to the user for approval.
- The user must explicitly approve the plan before the agent can proceed.