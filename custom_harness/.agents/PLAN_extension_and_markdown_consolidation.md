# Extension & Markdown Audit and Consolidation Plan

## Context Token Overhead & Audit Summary

An analysis of the active system prompt and extension files revealed that **customizations currently add ~7,100+ tokens to every single turn** in the context window:

1. **Always-On Rules**: `AGENTS.md` + 5 files in `.agents/rules/` = **~3,100 tokens** loaded into system instructions on every turn.
2. **Global Skill Header**: 55 skills registered in `~/.gemini/config/skills/` = **~4,000 tokens** loaded into system instructions on every turn.

This plan addresses both **Management Complexity** (Goal A) and **Context Overhead** (Goal B) through targeted rule consolidation, workspace-selective skill activation, source protection guardrails, and Git-backed state tracking.

---

## Key Design Principles

1. **Git-Backed Customization Manifest & Periodic Audit**:
   - **State in Git**: `.agents/customizations_manifest.json` tracks exactly which skills are enabled globally vs. per workspace.
   - **Restoration**: A simple script (`python3 .agents/scripts/sync_customizations.py`) restores your exact skill symlink configuration on any machine from Git.
   - **Periodic Audit**: The audit script calculates live context token overhead and warns you whenever context bloat exceeds defined thresholds.

2. **Per-Workspace Selective Skill Activation**:
   - `~/.gemini/skills/` serves as the central library storing all imported skills (unmodified).
   - `~/.gemini/config/skills/` holds core daily dev skills active across **all workspaces**.
   - Workspaces that need specialized GCP/ADK skills can selectively activate them by creating a symlink or folder in `<workspace-root>/.agents/skills/<skill-name>`.

---

## Proposed Changes

### Component 1: Workspace Rule Consolidation (Hybrid Strategy)

Currently, the workspace has 6 separate rule files loaded on every turn:
- `AGENTS.md` (722 tokens)
- `.agents/rules/zero_approval_spam_standards.md` (578 tokens)
- `.agents/rules/agent_safety_and_batch_standards.md` (380 tokens)
- `.agents/rules/standalone_customization_architecture.md` (324 tokens)
- `.agents/rules/cloudtop_git_velocity.md` (444 tokens)
- `.agents/rules/pragmatic_testing_standards.md` (859 tokens)

#### [MODIFY] [AGENTS.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/AGENTS.md)
Consolidate all essential, always-on core imperatives into a single, high-density `AGENTS.md` (~500 - 600 tokens total):
- **Core Bug Protocol**: `/bug`, `/list_bugs`, `/triage_bug`, `/fix_bug`
- **Checkpoint Protocol**: `/checkpoint` workflow
- **Zero Approval Spam**: Prefer native tools over terminal bash one-liners; write scratch scripts for complex data processing.
- **Git Velocity**: Compound bash commands for git operations (`git add && git commit && git push`).
- **Pragmatic Testing**: Implementation-first velocity; skip tests for docs/UI/minor edits; run targeted tests for logic changes.
- **Agent Safety**: Do not overwrite global config files directly.

#### [DELETE] [.agents/rules/zero_approval_spam_standards.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/rules/zero_approval_spam_standards.md)
Merged into core `AGENTS.md`.

#### [DELETE] [.agents/rules/agent_safety_and_batch_standards.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/rules/agent_safety_and_batch_standards.md)
Merged into core `AGENTS.md`.

#### [DELETE] [.agents/rules/standalone_customization_architecture.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/rules/standalone_customization_architecture.md)
Merged into core `AGENTS.md`.

#### [DELETE] [.agents/rules/cloudtop_git_velocity.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/rules/cloudtop_git_velocity.md)
Merged into core `AGENTS.md`.

#### [DELETE] [.agents/rules/pragmatic_testing_standards.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/rules/pragmatic_testing_standards.md)
Merged into core `AGENTS.md`.

**Token Savings**: **~2,500 tokens saved per turn** on always-on rules.

---

### Component 2: Global vs. Workspace-Selective Skill Architecture

#### 1. Central Skill Library (`~/.gemini/skills/`)
All imported skills remain untouched in `~/.gemini/skills/` as immutable sources of truth.

#### 2. Globally Active Core Skills (31 Symlinks in `~/.gemini/config/skills/`)
Symlinks active across **all workspaces**:
- **Conductor Workflow Suite**: `conductor-implement`, `conductor-new-track`, `conductor-revert`, `conductor-review`, `conductor-setup`, `conductor-status`
- **Bug & Task Management**: `bug`, `fix_bug`, `list_bugs`, `triage_bug`, `checkpoint`, `resume`
- **CLI & Execution Tools**: `gemini_cli`, `mcp_cli`, `colab`, `gemini-api-dev`, `gemini-interactions-api`, `gemini-live-api-dev`
- **Prompt & Quality Engineering**: `check_prompt`, `prompt_metrics`, `prompt_optimize`, `skill_readability`, `new_skill`, `skill-repair`, `progressive_disclosure_audit`, `find-skills`
- **Environment & Safety**: `accidental-data-loss-prevention`, `antigravity-guide`, `managing-python-dependencies`, `customerize`, `context_health`

#### 3. Workspace-Selective Specialized Skills (24 Skills in Library)
Unlinked from global `~/.gemini/config/skills/` (without deleting or modifying the underlying imported skill folders in `~/.gemini/skills/`), ready to be linked into specific workspace `.agents/skills/` as needed.

---

### Component 3: Workspace Markdown File Cleanup

#### [DELETE] [.agents/PLAN_transition_to_global_rule_and_sqlite.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/PLAN_transition_to_global_rule_and_sqlite.md)
- **Why Obsolete**: Temporary design plan artifact from a completed refactoring.

#### [DELETE] [.agents/prompt_heuristics.md](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/prompt_heuristics.md)
- **Why Obsolete**: Text export of `.agents/prompt_heuristics.json`.

---

### Component 4: State Management & Periodic Audit Tooling

#### [NEW] [.agents/customizations_manifest.json](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/customizations_manifest.json)
Git-tracked JSON file recording the exact state of active global skills, workspace-specific skills, and active rules.

#### [NEW] [.agents/scripts/sync_customizations.py](file:///home/brendanhills/dev/uk-bh-experiments/custom_harness/.agents/scripts/sync_customizations.py)
A lightweight Python CLI script that audits token overhead, syncs symlinks from `.agents/customizations_manifest.json`, and allows restoring setups instantly (`--restore`).

---

## Overall Expected Impact

- **Standard Workspace Token Load**: Reduced from **~7,100+ tokens** to **~2,600 tokens** per turn (**~63% context token reduction**).
- **Git Portability**: Skill and rule configuration saved directly in Git.
- **Automated Auditing**: Run `python3 .agents/scripts/sync_customizations.py --audit` at any time to audit token overhead.
