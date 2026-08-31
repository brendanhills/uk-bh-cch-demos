# Zero Approval-Spam Standards (Terminal Command & Script Execution)

In IDE and Cloudtop environments (like Jetski and Antigravity), security sandboxes require user approval for terminal command execution (`run_command`). Permission exceptions are matched by **command prefix or exact token matching**. 

These rules govern how AI agents execute commands and inspect data to prevent triggering repetitive, multi-line approval popups in the user UI.

## 1. Ban Inline One-Liners (`python3 -c` / `bash -c`) for Data Inspection
- **Constraint**: Agents must **NEVER** execute multi-line logic, file scanning, or data inspection using inline `python3 -c '...'` or `bash -c '...'` one-liners via terminal commands.
- **Why**: Every inline script contains different line numbers, variables, or logic strings, causing the IDE sandbox to evaluate every execution as a brand-new, unique command. Clicking *"always allow"* on an inline script only whitelists that exact multi-character string, making "always allow" useless and flooding the user with approval prompts.

## 2. Native Tools Exclusively for All File Operations (Zero Popups)
- **Constraint**: For searching, reading, filtering, creating, or editing `.json`, `.jsonl`, `.md`, `.ipynb`, or source code files, agents **MUST use native API tools** (`view_file`, `grep_search`, `code_search`, `list_dir`, `replace_file_content`, `write_to_file`, `notebook_edit`).
- **Protocol**: 
  - Never run `cat`, `sed`, `awk`, `grep`, `find`, or python reading/writing scripts in the terminal.
  - Native tools operate securely within workspace boundaries and **never trigger terminal command approval popups**.

## 3. Strict Scope for Helper Scripts
- **Constraint**: Do not create temporary or scratch Python/Bash scripts to perform tasks achievable with native tools.
- **Permitted Scripting**: Writing standalone scripts is only permitted when developing actual project deliverables or executing production data workflows (e.g., batch data processing scripts intended to be committed to the repository).
