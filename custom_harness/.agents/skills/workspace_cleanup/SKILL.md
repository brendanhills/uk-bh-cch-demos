---
name: workspace_cleanup
description: Audits workspaces for legacy, redundant, and obsolete files, safely relocates them into structured archive/ subdirectories with zero downtime, updates specifications and test references, verifies 100% test pass rates, and provides 1-command git rollback safety.
---

# 🧹 Workspace Cleanup & Legacy Archival Skill

Use this skill when a workspace has accumulated deprecated prototype files, superseded scripts, obsolete deployment helpers, redundant dataset mappings, or duplicate READMEs, and needs to be streamlined into a clean, minimal, turnkey production layout.

---

## 🎯 Core Operating Principles

1. **Zero Data Loss Invariant**: Never delete files permanently if they might contain historical context. Relocate candidate legacy files into clean, categorized `archive/` subdirectories (`archive/legacy_react_prototype/`, `archive/legacy_scripts/`, `archive/legacy_deploy/`, `archive/legacy_data/`, `archive/legacy_tools/`).
2. **Instant 1-Command Rollback Safety**: Always create a git safety checkpoint tag (`checkpoint-pre-archive-<YYYYMMDD>`) before moving or modifying any files.
3. **Spec-Driven Consistency**: Ensure that Master Specifications (`conductor/spec.md`, `tech-stack.md`), Conductor tracks, and Handover Guides are updated to remove stale references to archived files.
4. **Test Modernization & Zero-Regression Gate**: Modernize any outdated test assertions that read legacy paths so that 100% of the unit test suite passes cleanly after archival.

---

## 📋 Step-by-Step Execution Protocol

### Step 1: Deep Codebase & Dependency Audit
Scan the entire workspace and categorize all files into:
1. **Active Core Application / Frontend** (e.g. `index.html`, active JS/TS modules)
2. **Active Core Backend & Ingestion** (e.g. `server.py`, consolidated pipelines)
3. **Active Multi-Project Datasets** (e.g. `data/<project>/`)
4. **Active CI/CD & Deployment** (e.g. `Dockerfile`, `cloudbuild.yaml`)
5. **Active Automated Unit Tests** (e.g. `tests/test_*.py`)
6. **Active Specifications & Agent Rules** (`conductor/`, `.agents/`)
7. **Candidate Legacy / Redundant Files** (prototypes, unreferenced scripts, stale configs)

> [!TIP]
> Run the automated workspace clutter auditor helper script:
> ```bash
> python3 .agents/scripts/audit_workspace_clutter.py .
> ```

For each candidate legacy file, audit references across:
- Master Specs (`conductor/spec.md`, `conductor/tech-stack.md`, `conductor/product.md`)
- Conductor Tracks (`conductor/tracks/**/plan.md`, `conductor/tracks/**/spec.md`)
- Defect Registries (`.agents/bugs.json`)
- Runtime Imports (`server.py`, `scripts/`, `src/`)
- Unit Test Suites (`tests/`)

---

### Step 2: Calculate Reduction Delta & Propose Plan
Calculate the exact before vs. after file count reduction and directory tree impact. Present a structured proposal to the user with:
- Summary table of file counts by directory before vs. after cleanup.
- Target `archive/<category>/` folder mappings.
- Specific spec, test, and documentation files to update.
- Expected test suite pass rate.

*Always wait for explicit user approval before executing file moves.*

---

### Step 3: Create Safety Checkpoint Tag
Before moving any files, establish a clean rollback tag:

```bash
git tag -f -m "checkpoint before workspace cleanup" checkpoint-pre-archive-$(date +%Y%m%d)
```

---

### Step 4: Execute Structured Archival
Move candidate legacy files into structured `archive/` subfolders preserving git history:

```bash
mkdir -p archive/legacy_prototypes archive/legacy_scripts archive/legacy_deploy archive/legacy_data archive/legacy_tools

# Move tracked files via git mv (or mv for untracked files)
git mv <legacy-prototype-files> archive/legacy_prototypes/
git mv <superseded-scripts> archive/legacy_scripts/
git mv <obsolete-deploy-scripts> archive/legacy_deploy/
git mv <deprecated-data-files> archive/legacy_data/
git mv <stale-tools> archive/legacy_tools/
```

---

### Step 5: Modernize Specifications & Tests
1. **Master Specs & Tech Stack**: Update `conductor/spec.md` and `conductor/tech-stack.md` to reference the consolidated active modules and clean directory structure.
2. **README & Handover Guides**: Update root `README.md`, `Resume.md`, and operator runbooks. If duplicate READMEs exist in subdirectories, consolidate them into `docs/` and remove the subfolder README.
3. **Test Assertions**: Update any legacy test assertions that read deprecated paths to point to active dataset fixtures.

---

### Step 6: Full Verification & Walkthrough
Run the entire automated unit test suite to verify 100% pass rate:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Verify that the local development server starts and all REST endpoints return valid responses.

Generate a structured `walkthrough.md` artifact detailing:
- Total files removed/archived and percentage reduction in clutter.
- Structure of the `archive/` directory.
- Test verification output (100% OK).
- Exact 1-command rollback instructions:
  ```bash
  git checkout -f checkpoint-pre-archive-<YYYYMMDD>
  ```
