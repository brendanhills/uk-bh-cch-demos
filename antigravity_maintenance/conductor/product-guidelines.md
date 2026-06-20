# Product Guidelines: Antigravity Maintenance & Healing

These guidelines govern the design, implementation, and execution of diagnostics and repair utilities for the Google Antigravity environment.

---

## 1. Core Principles

### 1.1 Native-First Design (Resilience)
* **Standard Integration**: Always prioritize standard configurations and native settings over custom, invasive, or brittle wrappers.
* **No Side Effects**: Avoid modifications that would break during or after an official Antigravity software update.
* **Gcloud Dependency**: Leverage and default to native `gcloud` active configuration for GCP Project IDs when possible, ensuring compatibility with the rest of the Google Cloud SDK suite.

### 1.2 Non-Destructive Operations (Preservation)
* **Preserve Sessions**: Never modify, wipe, or move the active agent CLI session (`~/.gemini/antigravity-cli/`) or existing authentication states/transcripts.
* **Smart Backups**: Archive corrupted, stale, or conflicting configurations selectively into a dedicated, date-stamped backup folder (`~/.gemini-bak/`) before executing any write operations.
* **Selective Cleanup**: Target only verified stale processes or precise lock files (e.g., stale background language servers) during environment cleansing.

---

## 2. Diagnostics & Reporting Style

### 2.1 Unified Output Formatting
All automated diagnostic or repair scripts must output clear, actionable, and scannable status lines utilizing standard prefixes:
* `[+] SUCCESS`: For successfully verified components, repaired files, or cleared caches.
* `[-] FAILURE/ERROR`: For broken components, errors, or failed checks.
* `[!] WARNING/INFO`: For notable states, warnings about active processes, or non-destructive actions.

### 2.2 Transparency
* Every automated fix must output exactly *what* was modified, *why* it was modified, and *where* the backup of the original state was stored.

---

## 3. Maintenance Workflow

### 3.1 Step-by-Step Restoration
When recovering from system/plugin errors:
1. Run active process diagnostics to identify locks or stale threads.
2. Terminate background processes safely.
3. Perform non-destructive backup.
4. Auto-heal config structures (e.g., project IDs).
5. Load and verify plugins sequentially (one-by-one) to detect individual failure vectors.
