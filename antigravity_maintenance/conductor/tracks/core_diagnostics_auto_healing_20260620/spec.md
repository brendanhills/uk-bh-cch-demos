# Track Specification: Core Diagnostics & Configuration Healing

## 1. Objective
To construct a standalone, lightweight diagnostic and healing toolset capable of identifying stale language server and application background process locks, performing non-destructive configurations backups, and repairing blank/corrupted GCP Project ID configurations in Google Antigravity environments.

## 2. Requirements & Scope
* **Active Process Diagnostics**: Terminate background threads associated with `language_server` or `antigravity` cleanly and non-destructively.
* **Non-Destructive Backups**: Prior to any file repair, provide automated options to safely back up existing user configurations in `~/.gemini/` while fully preserving active transcripts and session directories (`~/.gemini/antigravity-cli/`).
* **Configuration Auto-Healing**: Verify and correct existing JSON project overrides under `~/.gemini/config/projects/` to ensure the `"enterpriseGcpProjectId"` is set to `"uk-bh-experiments-argolis"`.
* **Zero Dependency Policy**: Implement only using standard language runtimes and utilities (Bash and Python standard libraries only).

## 3. Architecture & Artifacts
The solution is split into two primary components:
1. **`fix_antigravity.sh`**: A shell-based entry point wrapper that handles terminal logs, detects and terminates stale process locks, and triggers the Python healing engine.
2. **`update_projects.py`**: A pure Python script that inspects workspace state databases, validates project files, and auto-heals GCP project properties.
