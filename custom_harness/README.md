# Custom Harness for Antigravity & Jetski

A modular harness for **Antigravity** and **Jetski** that deploys unified agent skills, plugins, lifecycle hooks, prompt heuristics, and global execution rules.

---

## 🚀 Quick Start (Setup on a New Machine)

To install all plugins, skills, hooks, prompt heuristics, and global rules on any new Cloudtop or developer machine:

```bash
# Global installation (recommended for all Antigravity & Jetski sessions)
./install.sh

# Or install locally scoped to a specific workspace
./install.sh --local /path/to/workspace
```

### What `./install.sh` Configures
- **Plugins**: Symlinks `.agents/plugins/` (and Conductor) to `~/.gemini/config/plugins/`.
- **Standalone Skills**: Deploys progressive disclosure skills to `~/.gemini/config/skills/`.
- **Global Rules**: Installs all `.md` rules from `.agents/rules/` into `~/.gemini/config/agents/rules/` and creates discovery symlinks in `~/.gemini/config/rules/`.
- **Direct File Editing Mandate**: Automatically verifies and appends the native tool editing mandate to `~/.gemini/config/AGENTS.md`.
- **Hooks & Scripts**: Deploys pre/post invocation hooks and diagnostic scripts into `~/.gemini/config/agents/`.
- **Prompt Heuristics**: Synchronizes core prompt guidelines and metrics.

---

## 🛡️ Direct File Editing & Anti-Scripting Mandate

To ensure deterministic edits, prevent approval popup spam, and eliminate buggy scratch scripts, all agents operating under this harness adhere to the **Direct File Editing Policy**:

### 1. Hard Prohibitions
- ❌ **No Shell File Manipulation**: `sed`, `awk`, `perl -pi`, `cat <<EOF >`, `echo "..." >`, and shell redirections are strictly banned for file reading or editing.
- ❌ **No Temporary File Scripts**: Agents must not create temporary Python or Bash scripts in `scratch/`, `/tmp`, or workspace directories simply to parse, search, or edit files.
- ❌ **No Inline Script One-Liners**: `python3 -c "..."` and `bash -c "..."` are prohibited for inspecting or modifying data.

### 2. Mandatory Native Tool Mapping Matrix

| Operational Goal | Required Tool | Prohibited Fallback |
| :--- | :--- | :--- |
| **Inspect / Read File Content** | `view_file` | `cat`, `head`, `tail`, Python file read scripts |
| **Search File Content / Code** | `grep_search` / `code_search` | `grep`, `rg`, `find | xargs` scripts |
| **List Directory Contents** | `list_dir` / `find_by_name` | `ls`, `find`, `tree` |
| **Localized Code / Text Edits** | `replace_file_content` | `sed -i`, `awk`, Python scripts |
| **New File Creation / Full Rewrites** | `write_to_file` (`Overwrite: true`) | `cat <<EOF >`, `echo >` |
| **Jupyter Notebook Edits (`.ipynb`)** | `notebook_edit` | `nbformat` / raw JSON scripts |

### 3. Edit Failure & Retry Protocol
If `replace_file_content` fails due to whitespace or matching discrepancies:
1. Re-read the target line range using `view_file` to obtain the verbatim ground truth.
2. Re-execute `replace_file_content` using the exact line chunk.
3. For large rewrites or structural changes, use `write_to_file` with `Overwrite: true`.
4. Agents must never fall back to terminal scripts or `sed` on edit errors.

---

## 📂 Repository Structure

```
custom_harness/
├── .agents/
│   ├── hooks/                   # Lifecycle hooks (e.g. check_prompt_heuristics.py)
│   ├── plugins/                 # Packaged plugins (bug_management, spec_drift)
│   ├── rules/                   # Universal agent rule definitions
│   │   ├── direct_file_editing_standards.md   # Anti-scripting & direct edit rules
│   │   ├── zero_approval_spam_standards.md    # Sandbox approval optimization
│   │   ├── agent_safety_and_batch_standards.md
│   │   ├── cloudtop_git_velocity.md
│   │   ├── pragmatic_testing_standards.md
│   │   └── standalone_customization_architecture.md
│   ├── scripts/                 # Maintenance, diagnostic, and metrics CLI utilities
│   ├── skills/                  # Standalone progressive disclosure skills
│   ├── prompt_heuristics.md     # Heuristics guidelines for prompt evaluation
│   └── hooks.json               # Hook definitions
├── conductor/                   # Conductor workflow extension submodule
├── install.sh                   # Universal global & local installer script
└── README.md                    # This documentation
```

---

## 🛠️ Single `dev` Branch & Subfolder Tagging Workflow

This repository follows the multi-project mono-branch standard on `dev`:
- Work is committed directly on the `dev` branch.
- Milestone checkpoints use subfolder-prefixed annotated tags: `custom_harness/checkpoint-YYYYMMDD-HHMM`.
- To checkpoint progress: run the `checkpoint` command to update tracking files, create the tag, and push upstream (`git push origin dev --tags`).
