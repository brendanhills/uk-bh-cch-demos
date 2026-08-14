# UK BH Experiments Monorepo (`uk-bh-experiments`)

A multi-project monorepo containing Google Cloud Customer Engineering prototypes, AI agent harnesses, customer demonstrations, and developer setup toolkits.

---

## 🛠️ Featured Developer Toolkits

| Toolkit | Description | Documentation |
| :--- | :--- | :--- |
| **[ce_chromebox_setup](ce_chromebox_setup/README.md)** | **Chromebook (Bruschetta) to Cloudtop remote development setup.** Single-touch Titan Key authentication, automated port conflict resolution, loop-protected background port tunnels (`9000`, `9090`, `8888`, `5387`), and rapid VS Code targeting. | [View Setup Guide](ce_chromebox_setup/README.md) |
| **[antigravity_suite](antigravity_suite/)** | Agent tooling, extensions, and workflow plugins. | [View Suite](antigravity_suite/) |
| **[custom_harness](custom_harness/)** | Custom evaluation and agent testing harnesses. | [View Harness](custom_harness/) |

---

## 🏛️ Monorepo Architecture

Each subfolder under `~/dev/uk-bh-experiments/*` represents an independent project workspace (e.g. `capita`, `BudgetDemo`, `custom_harness`, `HealthDirect`, `ce_chromebox_setup`).

To keep development clean, isolated, and easy to roll back across 40+ project subfolders, this repository enforces a **Single `dev` Branch + Path-Scoped Subfolder Tagging** workflow.

---

## 🌿 Core Development Workflow

### 1. Single `dev` Branch
- **All work occurs on the `dev` branch**.
- We do **not** create temporary feature or session branches.
- Commits are pushed directly to `origin/dev`.

### 2. Per-Project Conductor Setup
- Each customer or demo subfolder maintains its own independent `conductor/` directory (e.g. `capita/conductor/`, `custom_harness/conductor/`).
- Conductor tracks, specifications, implementation plans, and registry entries are isolated strictly within that subfolder.

### 3. Subfolder-Prefixed Git Tagging
Checkpoints, track starts, phase completions, and track finishes automatically create subfolder-prefixed Git tags on `dev`:

| Event | Tag Format Example | Purpose |
| :--- | :--- | :--- |
| **Session Checkpoint** | `capita/checkpoint-20260806-1400` | Mark end-of-session work for a subfolder |
| **Track Start** | `capita/auth-feature-start` | Record state before starting a track |
| **Phase Completion** | `capita/auth-feature-phase-1` | Record milestone at phase completion |
| **Track Completion** | `capita/auth-feature-complete` | Record state when track is fully verified |

---

## ↺ Path-Scoped Subfolder Restores & Reverts

Because all projects share the single `dev` branch, **repository-wide `git reset --hard` is strictly prohibited**. 

If something goes wrong in a specific project subfolder, you can restore **only that subfolder** back to a former tag or commit SHA without affecting any other project:

---

### Option A: Manual Terminal Commands (Without Conductor)

#### Step 1: Find the Tag (or Commit SHA)
```bash
# List all tags for your specific subfolder:
git tag -l "<subfolder>/*" --sort=-creatordate
```
> 💡 *If no tag was created, you can use `git log --oneline -- <subfolder>` to find any former commit SHA instead!*

#### Step 2: Restore the Subfolder
```bash
git restore --source=<tag_or_sha> -- <subfolder_path>
```
*Example:* `git restore --source=capita/checkpoint-20260806-1400 -- capita`

#### Step 3: Stage, Commit, and Push
```bash
git add <subfolder_path>
git commit -m "revert(<subfolder_path>): restore state to <tag_or_sha>"
git push origin dev
```

---

### Option B: Automated Reverts via Conductor
Run `/conductor:revert` inside the project chat. Conductor will present an interactive menu of recent tags and commit SHAs for `<subfolder_path>` and execute the path-scoped restore automatically.

---

## 🛠️ Slash Commands & Session Helpers

| Command / Skill | Description |
| :--- | :--- |
| `/checkpoint` | Commits work directly on `dev`, creates tag `<project>/checkpoint-YYYYMMDD-HHMM`, updates `resume.md` / `README.md`, and pushes `dev` + tags. |
| `/resume` | Verifies `dev` branch state, parses recent subfolder tags, and provides immediate onboarding to pick up work. |
| `/conductor:setup` | Initializes Conductor scaffolding inside the active subfolder (`<subfolder>/conductor/`). |
| `/conductor:new-track` | Plans a new track (spec + plan) and tags `<subfolder>/<track_id>-start`. |
| `/conductor:implement` | Executes track tasks, tags phase milestones, and tags `<subfolder>/<track_id>-complete`. |
| `/conductor:revert` | Path-scoped rollback/restore for a specific subfolder. |
| `/bug`, `/fix_bug`, `/list_bugs` | Bug management protocol (requires explicit `/fix_bug` for code edits). |

---

## 🐍 Python & Dependency Management

- **Always use `uv` and `pyproject.toml`** for Python environments and dependencies.
- **Never use `pip` and `requirements.txt`**.
