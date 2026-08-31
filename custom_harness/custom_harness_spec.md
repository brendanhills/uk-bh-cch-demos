---
name: custom_harness_spec
description: Functional specification for the Custom Harness project, optimizing Jetski and Antigravity for Google Cloud Customer Engineers (CEs) building customer demos, POCs, and AI prototypes.
files:
  - install.sh
  - README.md
  - Resume.md
  - .agents/rules/*.md
  - .agents/plugins/**/*
  - .agents/skills/**/*
---

# Custom Harness — Project Specification

## 1. Executive Summary & CE Design Philosophy

The **Custom Harness** is a modular developer extension, runtime configuration, and workflow accelerator for **Antigravity (IDE)** and **Jetski (Web/CLI)**. It is purpose-built to maximize **Google Cloud Customer Engineer (CE) productivity** when developing, updating, and iterating on customer demos, AI prototypes, and Proofs of Concept (POCs).

> [!NOTE]
> **Developer-Side Acceleration**: The harness is strictly an authoring and productivity accelerator for CEs during the design, coding, and scaffolding phases. It is not intended to run during live customer-facing demo deliveries.

### Core Architectural Principles
1. **Cross-Environment Parity (Antigravity & Jetski)**:
   - All harness capabilities, rules, and skills must function identically across both **Antigravity** (IDE) and **Jetski** (Web/CLI) without environment-specific crashes or divergence.
2. **Public Cloud & Flexible Tooling First**:
   - Standardizes on open, public tooling: **Git**, **Python managed strictly with `uv`** (mandate `uv` for virtual environments, package management, and running tools; never use raw `pip`), **gcloud CLI**, standard container/cloud deployments, and modern app frameworks (e.g. FastAPI, Streamlit, React, Vite, BigQuery, BigFrames as illustrative stack examples per demo need).
   - Direct integration with current **public Google Cloud APIs and AI SDKs** (including Alpha/Beta/Preview endpoints and Google ADK).
   - **Internal Tooling by Explicit Request Only**: Defaults to public standards, but allows individual customer/demo projects to opt into internal Google tooling (e.g. `project_dash` uses internal tools, while `CCH_demo` is purely public cloud).
3. **CE Development Velocity & State Isolation**:
   - **Minimized Approval Popup Friction**: Eliminate repetitive, meaningless permission prompts for routine file and read operations, selectively gating user approvals only for high-impact actions (breaking changes, destructive data operations, or major architectural shifts).
   - Deterministic direct file manipulation to eliminate broken helper scripts.
   - Isolated customer demo tagging (`<customer>/checkpoint-YYYYMMDD-HHMM`) on a unified `dev` branch.
4. **Progressive Disclosure Architecture**:
   - Minimizes static system prompt token bloat by loading lightweight skill descriptions globally, with detailed execution instructions retrieved only on-demand when commands are invoked.

---

## 2. System Topology & Deployment Architecture

### Directory Structure
```
custom_harness/
├── .agents/
│   ├── hooks/                   # Lifecycle hooks (e.g. check_prompt_heuristics.py)
│   ├── plugins/                 # Packaged multi-skill plugins (bug_management, spec_drift)
│   ├── rules/                   # Universal agent behavioral rule definitions
│   │   ├── direct_file_editing_standards.md
│   │   ├── zero_approval_spam_standards.md
│   │   ├── agent_safety_and_batch_standards.md
│   │   ├── cloudtop_git_velocity.md
│   │   ├── pragmatic_testing_standards.md
│   │   └── standalone_customization_architecture.md
│   ├── scripts/                 # CLI utilities (metrics, clutter audit, token sync)
│   ├── skills/                  # Standalone progressive disclosure skills
│   ├── prompt_heuristics.md     # Heuristics guidelines for prompt quality
│   └── hooks.json               # Hook definitions (PreInvocation / PostInvocation)
├── conductor/                   # Conductor workflow extension submodule
├── install.sh                   # Universal global and local installer script
├── README.md                    # Quick-start and documentation
└── Resume.md                    # Compaction and session recovery log
```

### Conductor Self-Isolation Guardrail
> [!WARNING]
> **Do NOT run the Conductor extension inside the `custom_harness` workspace.**
> Because `custom_harness` packages and installs Conductor itself, running a Conductor track inside `custom_harness` creates a circular development loop and state conflicts. Conductor is meant to be run in downstream demo/customer projects.

### Active Lifecycle Hooks (`.agents/hooks/`)
The harness currently deploys one active `PreInvocation` hook (`check_prompt_heuristics.py`) configured in `.agents/hooks.json`:
- Intercepts incoming user prompts to evaluate them against the 9 prompt heuristics.
- Injects non-intrusive ephemeral prompt refinement suggestions when prompts are underspecified.
- Asynchronously logs rule trigger metrics to `.agents/prompt_heuristics_log.jsonl`.

### Installation & Portability (`install.sh`)
- **Global Deployment (`./install.sh`)**:
  - Symlinks plugins to `~/.gemini/config/plugins/`.
  - Copies standalone skills to `~/.gemini/config/skills/`.
  - Copies rules to `~/.gemini/config/agents/rules/` and symlinks them to `~/.gemini/config/rules/`.
  - Idempotently ensures `~/.gemini/config/AGENTS.md` contains the Direct File Editing Mandate, Bug Workflow Scoping, and Checkpoint rules.
- **Local Deployment (`./install.sh --local <dir_path>`)**:
  - Installs self-contained plugins, skills, and rules directly into `<dir_path>/.agents/` for customer-shared workspaces.

---

## 3. Dynamic Agent Behavioral Invariants & Rule Contracts

The harness enforces a dynamic, extensible ruleset across `.agents/rules/`. Individual rules may be added, updated, or deprecated across iterations:

| Rule Document | Core Invariant & Behavioral Contract |
| :--- | :--- |
| **`direct_file_editing_standards.md`** | • **Strict Native Tool Mandate**: All reads, searches, creates, edits, and notebook changes must use `view_file`, `grep_search`, `list_dir`, `replace_file_content`, `write_to_file`, or `notebook_edit`.<br>• **Anti-Scripting Invariant**: Prohibits `sed`, `awk`, `cat <<EOF`, `echo >`, and temporary Python/Bash scripts for file operations.<br>• **Retry Protocol**: On replace match failure, re-read exact line range with `view_file` and retry. |
| **`zero_approval_spam_standards.md`** | • **Inline One-Liner Ban**: Prohibits `python3 -c` and `bash -c` one-liners (which generate unique hashes and spam terminal approval popups).<br>• **Native Tools First**: Prioritizes native tool APIs to eliminate sandbox popups. |
| **`agent_safety_and_batch_standards.md`** | • **Config Protection**: Agents must never attempt to bypass system protections on `AGENTS.md`.<br>• **Batch Resilience**: Multi-element batch loops must silently skip invalid/resolved items rather than halting.<br>• **Process Safety**: Process cleanup commands must walk the process tree and exclude ancestor shell PIDs to prevent killing the IDE or runner. |
| **`cloudtop_git_velocity.md`** | • **Compound Execution**: Git operations must be chained in a single bash command (`git add && git commit && git push`) within one tool call.<br>• **No Diagnostic Spam**: Prohibits redundant `git status` or `git config` queries before commits. |
| **`pragmatic_testing_standards.md`** | • **Implementation-First Velocity**: No default TDD for customer prototypes.<br>• **Skip Heuristic**: Skip automated tests for documentation, prompts, UI/styling, and trivial edits.<br>• **2-Retry Circuit Breaker**: Abort test harness setup debugging after 2 failed attempts. |
| **`standalone_customization_architecture.md`** | • **Symlink-Driven Global Sharing**: Enforces symlink deployment to prevent duplicate, out-of-sync files across workspaces. |

### Model Selection Policy (Always Use Current Generation Models)
- **Prohibition on Deprecated Models**: Agents must **never** default to obsolete or deprecated model versions (e.g. Gemini 1.x, 2.x, 3.1-flash, or deprecated model aliases).
- **Current Generation Standard**: Agents must always select the latest active production or current preview generation models specified for the platform.

---

## 4. Core Plugins & Progressive Disclosure Skills

### Packaged Plugins (`.agents/plugins/`)
1. **`conductor`** *(Git Submodule: `https://github.com/gemini-cli-extensions/conductor.git`)*:
   - Track-based project planning, specification decomposition, phased implementation, PSE-level code review, and rollback engine.
   - **Submodule Lifecycle & Updates**: Conductor upstream changes can be pulled and synchronized on demand via `git submodule update --remote conductor` or by running `./install.sh --update-submodules`.
2. **`bug_management`**: Structured Bug and Feature Request (FR) tracking backed by `.agents/bugs.json`, featuring non-destructive reporting (`/bug`, `/fr`), triage (`/triage_bug`), phased roadmapping (`/bug_plan`), audits (`/bug_review`), and TDD verification (`/fix_bug`).
3. **`spec_drift`**: Two-pass specification drift detection (`drift_detector.py` filter + LLM contract comparison) providing severity grading and ready-to-apply spec patch diffs.

### Standalone Progressive Disclosure Skills (`.agents/skills/`)
- **`workspace_cleanup`**: Automated discovery and safe structured archiving of legacy code and clutter with zero data loss.
- **`prompt_optimize` / `check_prompt` / `prompt_metrics`**: Prompt engineering evaluation against 9 core heuristics with SQLite metrics logging.
- **`mcp_cli`**: Model Context Protocol (MCP) server debugging and endpoint testing.
- **`customerize`**: Codebase auditing to identify internal Google dependencies and convert them to public Google Cloud equivalents.
- *(Optional / Utility)* **`colab`**: Infrequently used utility for exploratory Jupyter notebook editing and cell execution.

---

## 5. Specification Drift & Evolution Protocol

- Any future architectural modifications to `install.sh`, `.agents/rules/`, plugins, or skills should be evaluated against this human-approved specification using `/spec_drift`.
- In Spec-Driven Development (SDD), all proposed changes to architectural contracts must be reviewed and approved by the human engineer before adopting code or updating the specification.

---

## 6. Future Features & Roadmap

### 6.1 Tired Driver Detector (Fatigue & Adversarial Loop Sentinel)
- **Objective**: Detect when a developer has been working in extended continuous sessions and conversational interactions degrade into unproductive friction, repetitive corrections, or arguing with the AI rather than issuing structured, actionable engineering prompts.
- **Trigger Heuristics**:
  - High session turn count (>30+ turns without checkpointing or context resetting).
  - Repeated negative-sentiment phrasing, vague frustrated corrections ("no, fix it", "why did you do that again", "that's wrong"), or conversational thrashing across consecutive turns.
- **Remediation Protocol**:
  - Injects a gentle, non-intrusive ephemeral suggestion:
    * Recommends taking a short break.
    * Recommends saving session state via `/checkpoint`.
    * Suggests clearing conversational pollution with `/clear` to start fresh with a concise, anchored prompt.
