---
name: gemini-cli
description: >-
    Spawn gemini CLI subagents for parallel or isolated development tasks.
    Use when you need to run multiple coding tasks concurrently, set up
    implement-review loops, or offload work to keep the parent context
    window clean.
---

# Gemini CLI Subagent Development

Spawn isolated `gemini` CLI processes as subagents for parallel execution,
unbiased code review, or context-window management.

> [!IMPORTANT]
>
> **Prerequisite:** Install the `coding` extension per the
> [go/gemini-cli-extensions](http://go/gemini-cli-extensions) guide before using
> subagents for general google3 tasks.

## When to Use Subagents

-   **Parallel independent tasks** — e.g., fix 5 test files concurrently
-   **Implement→review loops** — reviewer doesn't know it wrote the code
-   **Context isolation** — offload noisy work without polluting your window
-   **Batch operations** — same action across many files/modules

## Spawning a Subagent

The gemini CLI binary lives at: `/google/bin/releases/gemini-cli/tools/gemini`

### Basic invocation

```bash
/google/bin/releases/gemini-cli/tools/gemini \
  --yolo \
  --model gemini-3-flash-preview \
  -e coding \
  -p 'Your prompt here'
```

| Flag                             | Purpose                                   |
| -------------------------------- | ----------------------------------------- |
| `--yolo`                         | Explicitly auto-approve all tool calls    |
| `-p` / `--prompt`                | Pass prompt as argument for headless      |
:                                  : (non-TUI) execution                       :
| `--model gemini-3-flash-preview` | Use Gemini 3.0 Flash (recommended         |
:                                  : default)                                  :
| `-e coding`                      | Enable coding (file read, workspace, CL   |
:                                  : creation)                                 :
| `-e none`                        | Disable all extensions (lightweight tasks |
:                                  : only)                                     :
| `-e ext1,ext2`                   | Enable specific extensions                |
| `--gfg`                          | Use Gemini for Google 3.1 Flash model     |
| `--allowed-tools t1 t2`          | Restrict available tools                  |
| `--project PROJECT`              | GCP project for quota (default:           |
:                                  : `shared-g3-gemini-quota`)                 :

> [!TIP]
>
> **`--yolo` is optional for subagents.** Without a tty, the CLI auto-detects
> non-interactive mode and proceeds without prompting. However, `--yolo` is
> recommended for predictability — it makes the intent explicit and avoids
> relying on tty-detection behavior that may change across CLI versions. Use
> `-p` to pass prompts for headless (non-TUI) execution. Without `-p`, the CLI
> defaults to interactive TUI mode.

### API Key

Not required, but if provided you can set `GEMINI_API_KEY` env var to pass in an
API key instead of relying on the default LOAS credentials.

```bash
GEMINI_API_KEY=your-key /google/bin/releases/gemini-cli/tools/gemini \
  --yolo --model gemini-3-flash-preview -e coding -p 'Your prompt'
```

### Extension selection

| Task                     | Extension         | Rationale                    |
| ------------------------ | ----------------- | ---------------------------- |
| Code edits, workspace/CL | `-e coding`       | Needs file access, Piper,    |
: creation                 :                   : Critique                     :
| Read-only analysis or    | `-e coding`       | Needs Codesearch, file       |
: review                   :                   : reading                      :
| Pure text generation (no | `-e none`         | Avoid unnecessary overhead   |
: tools)                   :                   :                              :
| Prevent recursive        | Omit subagent ext | Never pass your own subagent |
: subagents                :                   : extension                    :

### Allowed tools

#### Restrict available tools

Always attempt to restrict available tools, especially in `--yolo` mode. Select
tools which are needed by the subagent for the task at hand.

Example for an "investigation" subagent:

<!-- mdformat off -->

```bash
/google/bin/releases/gemini-cli/tools/gemini \
  --yolo --model gemini-3-flash-preview \
  -e coding \
  --allowed-tools read_file search_for_files_codesearch \
  -p 'Your prompt here'
```

<!-- mdformat on -->

#### Suggested `-e coding` tools

The `coding` extension provides MCP tools and disables problematic built-in grep
tools (`grep_search`, `glob`)

| Category      | Tools                                                     |
| ------------- | --------------------------------------------------------- |
| **Search**    | `search_for_files_codesearch`, `search_changelists`,      |
:               : `internal_search`                                         :
| **Buganizer** | `render_issue`, `get_bugs`, `add_buganizer_comment`,      |
:               : `create_buganizer_issue`, `list_components`               :
| **Piper/CLs** | `create_piper_workspace`, `list_piper_workspaces`,        |
:               : `get_current_workspace`, `create_changelist`,             :
:               : `update_changelist`, `update_changelist_reviewer`,        :
:               : `get_workspace_for_cl`                                    :
| **Critique**  | `get_critique_comments`, `get_critique_analysis`          |
| **Sponge**    | `read_sponge_test_logs`, `read_sponge_test_failure_logs`, |
:               : `list_sponge_artifacts`, `read_sponge_artifact`           :
| **YAQS**      | `render_question`, `search_questions`                     |

> [!TIP]
>
> Full extension config:
> `devtools/devassist/gemini_cli_for_google/extensions/coding/gemini-extension.json`

## Prompt Template

Structure every subagent prompt with these sections:

```
You are a subagent focused on [ROLE].

Your goal is to [SPECIFIC TASK].

Read the following skills before starting:
[SKILL.md paths if needed]

Working directory: [ABSOLUTE PATH]
Target file(s): [EXACT PATHS]
Verification: [EXACT TEST TARGETS OR COMMANDS]

Constraints:
- Do not delegate to another subagent.
- Do not modify files outside your scope.
- [Task-specific constraints]

Start the task now.
```

> [!IMPORTANT]
>
> Always include **exact file paths** and **verification commands**. Vague
> prompts like "fix all build errors" produce unreliable results.

## Common Orchestration Patterns

### Plan → Review → Fix

1.  Dispatch `planner` subagent to analyze and plan the work.
2.  Dispatch `reviewer` subagent to verify details.
3.  Dispatch `implementer` subagent to implement the plan.
4.  Repeat steps 2-3 until the plan is fully implemented and verified.

```
implementer('Add retry logic to auth.py, max 3 attempts')
  → reviewer('Verify auth.py retries exactly 3 times per spec')
  → reviewer finds 2 attempts → implementer('Fix: change to 3 attempts')
  → re-review passes ✅
```

### Parallel independent tasks

Dispatch multiple subagents when tasks don't share files:

```
# Good: separate files
subagent('Fix timeout in auth_test.cc')       # parallel
subagent('Fix memory leak in logger_test.cc')  # parallel
subagent('Fix flaky assertion in storage_test.cc')  # parallel

# Bad: same file → race condition
subagent('Add logging to server.cc')   # ❌ conflict
subagent('Add metrics to server.cc')   # ❌ conflict
```

### Workspace isolation for large edits

For massive parallel edits, use separate workspace clients:

```
subagent('In workspace agent_fix_1, fix auth module')
subagent('In workspace agent_fix_2, fix storage module')
# Optionally merge results afterward
```

## Constraints

-   **No file overlap** — never dispatch parallel agents to edit the same file
-   **No recursion** — never pass a subagent extension to the subagent; use `-e
    coding` (not your parent's full extension set)
-   **Timeouts** — default 20 minutes; adjust for long builds/tests
-   **Prompt specificity** — every subagent needs exact paths, targets, and
    success criteria
-   **Extension inheritance** — explicitly list extensions; subagents don't
    inherit the parent's extensions
-   **Context isolation** — subagents have no access to the parent's
    conversation history; pass all needed context in the prompt

## Reporting Issues

Report bugs or improvements for this skill at
[Agent Skill: gemini_cli](http://b/hotlists/8077919). See the `skill_issue`
skill for instructions on filing and triaging skill bugs.
