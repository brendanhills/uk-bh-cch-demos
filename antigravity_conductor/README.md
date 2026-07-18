# Conductor Workflows (Antigravity Extension)

Based on the original [Conductor Repository](https://github.com/gemini-cli-extensions/conductor) by the gemini-cli-extensions team.

**Measure twice, code once.**

Conductor is a workflow methodology that enables **Context-Driven Development** inside Antigravity. It turns your AI assistant into a proactive project manager that follows a strict protocol to specify, plan, and implement software features and bug fixes.

Instead of just writing code, Conductor ensures a consistent, high-quality lifecycle for every task: **Context -> Spec & Plan -> Implement**.

---

## 🚀 Feature Matrix: OOTB vs. Our Custom Enhancements

We have taken the core out-of-the-box (OOTB) Conductor capabilities and significantly upgraded them into an enterprise-grade, robust, and highly automated software engineering toolkit.

### 1. Core Out-of-the-Box (OOTB) Features

The foundational Conductor protocol provides structured tracking and spec-driven development:

*   **Context-Driven Setup (`/conductor:setup`)**: Interactive onboarding that configures `product.md`, `tech-stack.md`, `workflow.md`, and `product-guidelines.md` as the project's single source of truth.
*   **Spec & Plan Generation (`/conductor:newTrack`)**: Automatically initializes a track folder containing `spec.md`, `plan.md`, and `metadata.json` for any proposed feature, forcing architectural mapping before any coding begins.
*   **Protocol-Driven Implementation (`/conductor:implement`)**: An agent-guided execution loop that iterates over `plan.md` tasks sequentially, enforcing manual validation checks at phase boundaries.
*   **Automated Sync & Review (`/conductor:review`)**: Validates implemented features against your project standards and automatically updates high-level product specifications upon completion.
*   **Safe Reversion (`/conductor:revert`)**: Restores code and tracks registry to a clean previous checkpoint if a feature implementation is cancelled or fails verification.

---

### 2. Our Enhanced & Custom Added Features (New!)

To support complex developer setups, fast bug fixes, and rigorous command safety, we designed and built these powerful new modules:

#### A. Centralized Multi-Runner Installation & Removal
*   **Global Plugin Installer (`./install_conductor.sh`)**: Symmetrically copies the Conductor extension to both the system extension directory (`~/.gemini/config/plugins/conductor`) and the CLI configuration directory (`~/.gemini/antigravity-cli/plugins/conductor`). It automatically compiles and installs all 10 global workflows to ensure absolute consistency in `agy`, `antigravity-cli`, `antigravity-x64`, etc.
*   **Surgical Uninstaller (`./uninstall_conductor.sh`)**: Symmetrically purges Conductor from both system and CLI plugin directories, and cleanly removes all Conductor global workflow files while leaving other custom tools untouched.

#### B. Lightweight Bug Tracking System
*   **`/conductor:bug <description>`**: Quickly flag a bug. Prompts for **Impact** and **Priority**, automatically calculates the next ID, records current timestamps and workspace paths, and writes directly to `.agents/bugs.json`.
*   **`/conductor:bug-list [all]`**: Generates a clean markdown table of unresolved bugs grouped by priority, with `P0` listed at the top. Append `all` to show completed/closed items.
*   **`/conductor:bug-triage [id]`**: Opens an interactive, guided CLI wizard allowing developers to adjust priority, modify the description, or advance the bug's status (`New` $\rightarrow$ `Investigating` $\rightarrow$ `Fix Implemented` $\rightarrow$ `Fix Verified` $\rightarrow$ `Closed`).
*   **`/conductor:bug-fix <id>`**: Bypasses heavy track folder overhead. Directly guides the agent to locate the code defect, implement the fix, run workspace tests to verify success, and immediately mark the bug as `"Fix Implemented"`.

#### C. Unified Dashboard Integration (`/conductor:status`)
*   **Bugs Aggregation**: Automatically scans your workspace for `.agents/bugs.json` and parses it on-the-fly.
*   **Metrics & Blockers**: Merges track progress metrics with your active bugs. The status report now lists the count of unresolved bugs, breakdown by priority (`P0: X | P1: Y ...`), and a bulleted list of active `P0/P1` items serving as critical blockers.

#### D. Automated Validation & Testing Harnesses
*   **TOML Structure Validator (`test_conductor_validation.py`)**: Automatically asserts that all commands under `commands/` have description and prompt metadata, conform to standard layout rules (including `SYSTEM DIRECTIVE` and `SETUP CHECK` headings), and map correctly to corresponding Markdown workflow files in `workflows/`.
*   **Workspace Integrity & Schema Validator (`test_workspace_validation.py`)**: Validates the structural health of your workspace. It parses `.agents/bugs.json` to enforce strict formatting and valid statuses/priorities, and scans `conductor/tracks.md` to flag broken links, empty directories, or missing spec files.

#### E. End-of-Session Checkpoint Tooling
*   **`/conductor:checkpoint`**: Automatically performs your end-of-session handoff workflow right from within the Conductor command system. It checks Conductor tracks status, audits recent Git diffs, updates `README.md` dynamically, writes/overwrites a durable session `resume.md` handoff file, commits all changes (auto-branching off main/master if needed), and offers to push to origin!

---


## 📁 Repository Structure

```
.
├── commands/                  # Conductor TOML command definitions
│   ├── bug.toml               # (New!) /conductor:bug definition
│   ├── bugFix.toml            # (New!) /conductor:bug-fix definition
│   ├── bugList.toml           # (New!) /conductor:bug-list definition
│   ├── bugTriage.toml         # (New!) /conductor:bug-triage definition
│   ├── checkpoint.toml        # (New!) /conductor:checkpoint definition
│   ├── status.toml            # (Enhanced) Unified dashboard status command
│   └── ...                    # Other core commands (setup, implement, etc.)
├── workflows/                 # Markdown wrapper files for slash commands
│   ├── conductor-bug*.md      # (New!) Bug tracking workflow files
│   ├── conductor-checkpoint.md # (New!) Checkpoint session workflow file
│   └── ...                    # Core workflow files
├── tests/                     # Validation suite
│   ├── test_syntax.py         # OOTB syntax validator (JSON/TOML/MD)
│   ├── test_conductor_validation.py  # (New!) Command structure validator
│   └── test_workspace_validation.py  # (New!) Active workspace integrity checker
├── install_conductor.sh       # (New!) Global multirunner setup script
├── uninstall_conductor.sh     # (New!) Symmetrical uninstaller script
├── setup_conductor.sh         # Symlinks workspace commands into global workflows
└── sync_conductor_github.sh   # Slices upstream changes with local customizations
```

---

## ⚙️ Prerequisites

*   **uv** (Recommended python package and environment manager: https://github.com/astral-sh/uv)
*   **Python 3.11+**
*   **PyTest** (Managed automatically if using `uv`)

---

## 🛠️ Getting Started

### 1. Install Globally (Run Once)
To install the Conductor plugin and register all the OOTB and enhanced workflows across all your runners:
```bash
./install_conductor.sh
```

### 2. Verify Your Configuration
Run the automated testing suite at any time to verify that your workflows and commands conform perfectly to standard Conductor rules:
```bash
uv run pytest tests/
```

### 3. Uninstall Globally
To completely clean out and remove Conductor and its global workflows:
```bash
./uninstall_conductor.sh
```

---
*Maintained as part of the UK-BH experiments for agentic workflow automation.*
