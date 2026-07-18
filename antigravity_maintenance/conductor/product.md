# Initial Concept

The goal of this project is to create guidelines and a diagnostic/repair plan based on Conductor for fixing and maintaining Google Antigravity environments and configurations. This will serve as a centralized, systematic framework to troubleshoot, heal, and resolve configuration conflicts (such as missing project IDs, environment path mismatches, or corrupted caches) whenever they occur.

# Product Guide: Antigravity Maintenance & Healing

## 1. Vision Statement
To establish a robust, reliable, and completely standardized system and plan for diagnosing, repairing, and maintaining Google Antigravity environments and configurations. This framework ensures that any configuration failures, empty project ID crashes, or plugin load errors are handled systematically with zero-risk to active user sessions and complete alignment with standard Google Cloud configurations.

## 2. Core Features & Capabilities
* **Active Process Diagnostics**: Automated detection and safe termination of stale, background `language_server` or `antigravity` processes causing cache lockups or file synchronization blocks.
* **Lightweight Configuration Auto-Healing**: A standalone Python utility to scan recent workspace history and dynamically generate/repair project-level files with correct GCP project IDs (`uk-bh-experiments-argolis`).
* **Zero-Touch Native Fallbacks**: Safe reliance on local `gcloud` configuration defaults and Settings UI, avoiding complex custom wrappers that could break during future application updates.
* **Preservation-First Backups**: Selective backup routines that safely archive corrupted states (to `~/.gemini-bak/`) while leaving active agent sessions (`antigravity-cli/`) and authentication tokens untouched.

## 3. Target Audience & Environment
* **Platform**: Linux (primarily target environments running standard bash shell environments).
* **Users**: Power-users and developers (like Captain B) running Antigravity CLI (`agy`), Antigravity IDE, or Antigravity 2.0 parallel desktop applications.

## 4. Key Use Cases
* **Empty Project ID Recovery**: Resolving the immediate `invalid project ID: ""` error when launching an agent.
* **Prustine Re-Initialization**: Performing a complete reset of application configurations while preserving active transcripts and active login sessions.
* **Plugin Troubleshooting**: Systematically validating and restoring vital plugins (like `conductor`) one-by-one to identify and prevent corruption vectors.
