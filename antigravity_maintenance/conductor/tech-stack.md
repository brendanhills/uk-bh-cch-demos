# Technology Stack: Antigravity Maintenance & Healing

This document outlines the selected technology stack and system dependencies for our Antigravity Maintenance & Healing framework.

---

## 1. Core Languages & Runtime
* **Python (3.10+)**: Primary language for robust file parsing, system automation, and structural configuration healing.
* **Bash Shell (4.0+)**: Primary scripting interface for quick environment diagnostics, script execution wrapper, and local process management.

## 2. Configuration Parsing, Validation & Healing
* **Python Standard Library Only**:
  - `json`: To safely read, validate, and write JSON configuration overrides in `~/.gemini/config/projects/`.
  - `sqlite3`: To inspect and manipulate local configuration database states (like local workspace caches).
  - `re`: For regular expression validation and matching project IDs.
  - `os` / `pathlib`: For robust cross-path resolution and file operations.

## 3. Reporting & Diagnostics Logging
* **Standard Console Output**: Console output utilizes standard ANSI escape codes for coloring.
* **Scannable Unified Prefix System**:
  - `[+] SUCCESS` (Green ANSI)
  - `[-] FAILURE/ERROR` (Red ANSI)
  - `[!] WARNING/INFO` (Yellow/Blue ANSI)
* **Offline Logs**: Run transcripts and error logs are captured into plain-text files inside the logs directory for persistence.

## 4. Backup & Process Management
* **Native Process Diagnostics**: Uses standard Linux command utilities (`lsof`, `ps`, `pkill`, `kill`) via Python `subprocess` modules to accurately identify and safely terminate stale background processes.
* **Native Backups**: Leverages standard Linux `tar` and `gzip` commands or python's `shutil` module to perform selective, non-destructive archives of `~/.gemini/` prior to any healing action.
