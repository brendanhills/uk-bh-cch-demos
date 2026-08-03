# Antigravity Suite

A consolidated, premium, and unified developer extension, diagnostics, and maintenance suite for **Antigravity** and **Jetski**.

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
