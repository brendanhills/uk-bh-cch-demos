# Conductor Workflows (Jetski Extension)

Based on the original [Conductor Repository](https://github.com/gemini-cli-extensions/conductor) by the gemini-cli-extensions team.

**Measure twice, code once.**

Conductor is a workflow methodology that enables **Context-Driven Development**. It turns your AI assistant into a proactive project manager that follows a strict protocol to specify, plan, and implement software features and bug fixes.

Instead of just writing code, Conductor ensures a consistent, high-quality lifecycle for every task: **Context -> Spec & Plan -> Implement**.

The philosophy is simple: by treating context as a managed artifact alongside your code, you transform your repository into a single source of truth that drives every agent interaction with deep, persistent project awareness.

## 🚀 Features

### 📋 Conductor Methodology Features
- **Context-Driven Development**: Treat context as a managed artifact (Product, Tech Stack, Guidelines).
- **Plan Before You Build**: Automated generation of `spec.md` and `plan.md` for tracks.
- **Safe Iterations**: Manual verification checkpoints at phase ends.

### 🛠️ Jetski Workflow Features (This Repo)
- **Upstream Synchronization**: `./sync_conductor_github.sh` checks for reference updates without clobbering local defaults.
- **Syntax Verification Tests**: Automated PyTest suite (`tests/test_syntax.py`) to validate all `.toml` and `.md` files.
- **Local Workspace Setup**: `./setup_workflows.sh` to symlink commands into your Jetski runtime.

## 📁 Repository Structure

- `commands/`: Conductor command definitions (e.g., `setup.toml`, `newTrack.toml`).
- `policies/`: Jetski tool usage policies (permits Plan Mode edits).
- `tests/`: PyTest validation suite using Python's `tomllib`.
- `sync_conductor_github.sh`: Script to automatically fetch upstream changes and verify against local customizations.
- `setup_workflows.sh`: Symlinks local workflows into the Jetski runtime environment.

## ⚙️ Prerequisites

- **Python 3.11+** (for standard `tomllib` parsing)
- **PyTest** (for verification suite)
- **Git** (for sync script cloning)

## 🛠️ Usage

### 1. Setup Local Symlinks
To link these workflows into your global Jetski environment, run:
```bash
./setup_workflows.sh
```

### 2. Set Up the Project (Run Once)
When you run `/conductor-setup`, Conductor helps you define the core components of your project context.

- **Product**: Define project context (e.g., users, goals, features).
- **Product guidelines**: Define standards (prose style, branding).
- **Tech stack**: Configure technical preferences (languages, frameworks).
- **Workflow**: Set team preferences (TDD, commit strategy).

**Generated Artifacts:**
- `conductor/product.md`
- `conductor/product-guidelines.md`
- `conductor/tech-stack.md`
- `conductor/workflow.md`
- `conductor/code_styleguides/`
- `conductor/tracks.md`

```bash
/conductor-setup
```

### 3. Start a New Track (Feature or Bug)
When you’re ready to take on a new feature or bug fix, run `/conductor-new-track`. This initializes a **track** — a high-level unit of work.

- **Specs**: The detailed requirements for the specific job. What are we building and why?
- **Plan**: An actionable to-do list containing phases, tasks, and sub-tasks.

**Generated Artifacts:**
- `conductor/tracks/<track_id>/spec.md`
- `conductor/tracks/<track_id>/plan.md`
- `conductor/tracks/<track_id>/metadata.json`

```bash
/conductor-new-track
# OR with a description
/conductor-new-track "Add a dark mode toggle to the settings page"
```

### 4. Implement the Track
Once you approve the plan, run `/conductor-implement`. Your coding agent then works through the `plan.md` file, checking off tasks as it completes them.

```bash
/conductor-implement
```

Conductor will:
1. Select the next pending task.
2. Follow the defined workflow (e.g., TDD).
3. Verify progress at the end of each phase.

### 5. Check Status, Review, and Revert
- **Check status**: Get a high-level overview of project progress.
  ```bash
  /conductor-status
  ```
- **Review work**: Review completed work against guidelines and the plan.
  ```bash
  /conductor-review
  ```
- **Revert work**: Undo a feature or a specific task if needed.
  ```bash
  /conductor-revert
  ```

## 🔍 Upstream Verification

To fetch the latest reference features from GitHub and review diffs without overriding your customizations:
```bash
./sync_conductor_github.sh
```
*Outputs will be saved to `diff_report.txt`.*

To run syntax validation tests:
```bash
pytest tests/test_syntax.py
```

---
*Maintained as part of the UK-BH experiments for agentic workflow automation.*
