# Antigravity Suite

A consolidated, premium, and unified developer extension, diagnostics, and maintenance suite for **Antigravity** and **Jetski**.

> [!WARNING]
> **Do NOT use the Conductor extension in this project.**
> The Conductor submodule and its skills are tracked solely for diagnostic and backwards-compatibility check-ups, but must never be executed or active.

---

## 📂 Suite Structure

- **`install.sh`**: The centralized entrypoint for all operations (installing, diagnosing, and repairing).
- **`conductor/`**: Centralized Conductor submodule.
- **`harness/`**: Core progressive disclosure skills and agent rules.
- **`maintenance/`**: Diagnostic and configuration repair scripts.
- **`.agents/`**: Workspace-level rules, prompt heuristics, and metrics configurations.

---

## 🚀 Usage Guide

All operations are coordinated through the root `install.sh` runner:

### 1. Perform Global Installation
Deploys all harness skills, Conductor skills, and system hooks globally to your `~/.gemini/` configuration:
```bash
./install.sh
```

### 2. Run Diagnostics & Integrity Checks
Verifies that all skills, directories, and dependencies are correctly installed and synchronized with the latest version:
```bash
./install.sh --diagnose
```

### 3. Diagnose and Repair Errors
Terminates orphan language server or Antigravity processes and synchronizes Google Cloud project configurations globally to prevent `invalid project ID: ""` errors:
```bash
./install.sh --repair
```

### 4. Help Menu
View all command options:
```bash
./install.sh --help
```

---

## 🛡️ Safety Updates

### August 2026: Safe Diagnostics and Repair
- **Safe Process Targeting:** Resolved an issue where running `./install.sh --repair` would abruptly kill the active Antigravity GUI/IDE and other terminal processes, resulting in a core dump.
- **Path Isolation:** Switched from matching processes on full command-line arguments (which caused path-name collisions with workspaces named `antigravity_suite`) to matching only on the specific binary/executable name (`comm`).
- **IDE Preservation:** Restricted process termination exclusively to `language_server` instances. The main `antigravity` editor process is now entirely untouched, guaranteeing session stability during configuration repairs.

