# Direct File Editing & Manipulation Standards

AI agents (Jetski, Antigravity) must interact with project files, source code, documentation, and configuration files **exclusively through native tool APIs**.

---

## 1. Strict Prohibition of Shell File Manipulation & Scratch Scripts
- **NEVER use shell commands to read or modify files**: Prohibit `sed`, `awk`, `perl -pi`, `cat << 'EOF' >`, `echo "..." >`, `printf >`, `patch`, and `truncate` via `run_command`.
- **NEVER create helper or scratch scripts for file operations**: Do NOT generate temporary Python, Node.js, or Bash scripts (in `scratch/`, `/tmp`, or workspace directories) solely to read, parse, search, regex-replace, or edit files.
- **NEVER use inline script execution**: Do NOT run `python3 -c "open('file.txt', 'w').write(...)"` or `bash -c` one-liners to perform file edits or data extraction.

---

## 2. Mandatory Native Tool Mapping Matrix

| Operational Goal | Required Tool | Prohibited Fallback |
| :--- | :--- | :--- |
| **Inspect / Read File Content** | `view_file` | `cat`, `head`, `tail`, Python file read scripts |
| **Search File Content / Code** | `grep_search` / `code_search` | `grep`, `rg`, `find | xargs` scripts |
| **List Directory Contents** | `list_dir` / `find_by_name` | `ls`, `find`, `tree` |
| **Localized Code / Text Edits** | `replace_file_content` | `sed -i`, `awk`, Python scripts |
| **New File Creation / Full Rewrites** | `write_to_file` (`Overwrite: true`) | `cat <<EOF >`, `echo >` |
| **Jupyter Notebook Edits (`.ipynb`)** | `notebook_edit` | `nbformat` / raw JSON scripts |

---

## 3. Error Recovery & Edit Failure Protocol
If `replace_file_content` fails (e.g., TargetContent match failure, line range misalignment, or whitespace discrepancies):
1. **Re-Read the Target Region**: Call `view_file` specifying the exact line range `[StartLine, EndLine]` to fetch the ground-truth text, including leading whitespace and indentation.
2. **Re-Execute `replace_file_content`**: Update `TargetContent` with the exact verbatim string returned by `view_file`.
3. **Full Overwrite Protocol**: If the file is small or structural refactoring makes incremental replacement inefficient, use `write_to_file` with `Overwrite: true`.
4. **NO SCRIPT FALLBACK**: Under no circumstances should a failed native edit trigger the generation of a `sed` command or Python script.

---

## 4. Legitimate Terminal Execution Boundaries
The `run_command` tool is strictly reserved for:
- Running build tools, compilers, and linters (e.g., `blaze build`, `npm run build`, `tsc`).
- Executing project test suites (e.g., `pytest`, `cargo test`, `go test`).
- Version control and deployment commands (e.g., `git`, `gcloud`, `terraform`).
- Executing established application binaries and production CLI utilities.
