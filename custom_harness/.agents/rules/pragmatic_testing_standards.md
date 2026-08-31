# Pragmatic Testing & Verification Standards (Normal Chat & Coding)

These rules govern how AI agents handle testing, TDD, and verification during everyday "normal" chat, coding tasks, feature implementations, and refactoring across all workspaces.

## 1. Implementation-First Velocity (No Default TDD)
- **Constraint**: Do NOT adopt a Test-Driven Development (TDD) or "test-first" workflow by default in normal chat unless explicitly commanded by the user.
- **Protocol**: Implement the actual application code changes first. Do not block progress trying to bootstrap new test harnesses or complex mocking frameworks from scratch.

## 2. Test Execution Heuristics Matrix (When to Run Tests vs. When to Skip)

### Tier 0: Skip Automated Tests Entirely (~80% of tasks)
Do **NOT** run any automated tests (`pytest`, `go test`, `npm test`, etc.) for:
- **Documentation & Prompts**: Editing Markdown (`README.md`, SDDs, docstrings), Agent Skills (`SKILL.md`), or AI prompt templates.
- **Configs & Formatting**: Editing `.gitignore`, linter rules, formatting, or simple environment/YAML configs.
- **Frontend UI & CSS Styling**: Editing HTML/CSS templates, layout styles, color schemes, or popups (e.g., `index.html`). Validate via direct browser view (e.g., `http://localhost:9000/rch/`) instead of running backend Python test suites.
- **Lightweight / Trivial Code Edits**: Minor 1–5 line localized changes (typo fixes, string updates, log message improvements, or simple variable renames).
- **Dead Code Cleanup**: Deleting unused imports or commented-out code.
- **User Override**: Whenever the user says *"just make the change"*, *"quick edit"*, or *"don't run tests"*.

### Tier 1: Targeted Fast-Path Execution (< 5 seconds — ~15% of tasks)
Run **only a single specific test file or individual function** (e.g., `pytest path/to/test_foo.py -k test_my_func`) **ONLY** when:
- **Isolated Business Logic Change**: Modifying non-trivial algorithmic logic in a single file where an obvious matching `test_<file>.py` exists right next to it.
- **Constraint**: Total execution time must be under **5 seconds**. Never invoke an entire module folder if a single file or function can be targeted.

### Tier 2: Broad / Regression Suite Execution (~5% of tasks)
Run a wider regression or module test suite **ONLY** when:
- **Core Shared Architecture Refactoring**: Modifying a core shared library, base class, database schema, or public API contract used across 3+ different modules.
- **Explicit User Command**: When the user explicitly requests: *"run tests"*, *"verify tests pass"*, or *"check for regressions"*.

## 3. The 2-Retry Test-Debugging Circuit Breaker (Anti-Loop Guardrail)
- **Constraint**: If an agent attempts to run or add a test and encounters test-harness failures, import errors, or fixture/mocking bugs, **it has a strict maximum of 2 retry attempts** to fix the test setup.
- **Circuit Breaker**: If a test still fails after **2 retries** due to harness or mocking setup (rather than a clear logic bug in the application code), **THE AGENT MUST STOP DEBUGGING THE TEST IMMEDIATELY**.
- **Remediation Protocol**:
  1. Revert the broken test case edit or stop running the broken test harness.
  2. Inform the user: *"The test harness requires complex mock bootstrapping. I have verified the implementation directly and avoided further test debugging."*
  3. Continue session progress without wasting tokens or user patience.
