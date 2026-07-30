# Zero Approval-Spam Standards (Terminal Command & Script Execution)

In IDE and Cloudtop environments (like Jetski and Antigravity), security sandboxes require user approval for terminal command execution (`run_command`). Permission exceptions are matched by **command prefix or exact token matching**. 

These rules govern how AI agents execute commands and inspect data to prevent triggering repetitive, multi-line approval popups in the user UI.

## 1. Ban Inline One-Liners (`python3 -c` / `bash -c`) for Data Inspection
- **Constraint**: Agents must **NEVER** execute multi-line logic, file scanning, or data inspection using inline `python3 -c '...'` or `bash -c '...'` one-liners via terminal commands.
- **Why**: Every inline script contains different line numbers, variables, or logic strings, causing the IDE sandbox to evaluate every execution as a brand-new, unique command. Clicking *"always allow"* on an inline script only whitelists that exact multi-character string, making "always allow" useless and flooding the user with approval prompts.

## 2. Native Read-Tools First (Zero Popups)
- **Constraint**: For searching, reading, filtering, or checking `.json`, `.jsonl`, `.md`, or source code files, agents **MUST use native API tools** (`grep_search`, `view_file`, `code_search`, `list_dir`) first.
- **Protocol**: Never run `cat`, `grep`, `find`, or python reading scripts in the terminal if a native API read tool can accomplish the task. Native read tools operate securely within workspace boundaries and **never trigger a terminal command approval popup**.

## 3. Write Standalone Scripts to `scratch/` for Programmatic Execution
- **Constraint**: When custom Python or Bash data analysis is genuinely required (e.g., parsing complex JSONL structures or custom aggregations):
  1. Write the code cleanly to a standalone script file first (e.g., `scratch/inspect_data.py` or `scripts/validate.py`) using `write_to_file`.
  2. Execute the file using a clean, stable terminal command:
     ```bash
     python3 scratch/inspect_data.py
     ```
- **Why**: When executing a stable file path, the command prefix (`python3 scratch/inspect_data.py` or `python3 scratch/`) remains constant. The user only has to approve the prefix once per project or conversation, eliminating approval spam entirely.
