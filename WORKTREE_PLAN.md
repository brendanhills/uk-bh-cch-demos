# Fixed Worktrees Strategy for Multi-Project Monorepo

> [!NOTE]
> **Status**: Planned for future implementation.

## Overview & Problem Statement
Currently, all projects and customer subfolders in `uk-bh-experiments` share a single Git working directory tree. When working on 3–4 projects/customers concurrently in Antigravity or Jetski, changing or creating a Git branch in one project switches the branch across the entire repository. This leads to accidental commits from one project bleeding into another project's branch.

To solve this **without creating many temporary branch folders on disk**, we will set up **Fixed Persistent Worktree Directories** (one per active project/customer).

---

## Safety & Non-Disruption Guarantees

> [!IMPORTANT]
> **Zero Risk to Existing Projects**: Your existing primary repository at `/home/brendanhills/dev/uk-bh-experiments` remains **100% untouched, unchanged, and intact**. Nothing is moved, renamed, or converted. You can continue opening and working in your primary repo directory exactly as you do today.

---

## Fixed Worktree Architecture (2–3 Folders Total)

Instead of creating a new folder for every new feature branch, you keep **fixed, persistent workspace folders** on disk for the projects you are actively working on:

```text
~/dev/
├── uk-bh-experiments/                            # Main monorepo working tree (UNTOUCHED)
│   ├── BudgetDemo/
│   ├── capita/
│   └── custom_harness/
│
├── uk-bh-experiments-capita/                     # Fixed workspace for Capita
│   └── capita/                                   <-- Open in Antigravity / Jetski
│                                                     (Switch/create/push/rollback any capita/* branch here)
│
└── uk-bh-experiments-budget/                     # Fixed workspace for BudgetDemo
    └── BudgetDemo/                               <-- Open in Antigravity / Jetski
                                                      (Switch/create/push/rollback any budget/* branch here)
```

### Key Benefits:
1. **No Folder Proliferation**: You only have 2–3 fixed folders total on disk. No temporary folders created or deleted when making branches.
2. **Dedicated IDE Windows**: Open `~/dev/uk-bh-experiments-capita/capita` in one Antigravity window and `~/dev/uk-bh-experiments-budget/BudgetDemo` in another.
3. **Independent Branch Control**: You can checkout, create, push, or roll back branches inside `uk-bh-experiments-capita` without ever affecting the branch or working files in `uk-bh-experiments-budget` or `uk-bh-experiments`.
4. **Targeted Rollbacks**: Commits on `capita/*` branches touch only `capita/`. If you roll back Capita changes, BudgetDemo is completely unaffected.

---

## Proposed Solution Architecture

### 1. Transparent Shell Helper Functions (`~/.bashrc` / `~/.zshrc`)
We will add thin, explicit shell functions to easily set up or switch fixed project worktrees:

* `gw-init <project-folder>` (e.g. `gw-init capita`):
  - Creates the fixed worktree directory `~/dev/uk-bh-experiments-<project-folder>` if it doesn't exist yet.
  - Symlinks shared `.venv` or `.env` if present.
  - Opens `~/dev/uk-bh-experiments-<project-folder>/<project-folder>` directly in Antigravity / Jetski.

* `gw-commit [commit-message]`:
  - Automatically stages ONLY files within the active project subfolder (`git add <project-folder>`).
  - Executes `git commit -m "[commit-message]"`.

* `gw-ls`:
  - Displays all active worktrees and their current checked-out branches.

### 2. Native Git Aliases (`~/.gitconfig`)
For direct Git usage:
* `git wt-ls`: `git worktree list`
* `git wt-add`: `git worktree add`
* `git wt-rm`: `git worktree remove`
* `git wt-prune`: `git worktree prune`

---

## Planned Implementation Steps

1. Add `gw-init`, `gw-commit`, `gw-ls` shell helpers to `~/.bashrc` or `~/.zshrc`.
2. Configure `wt-*` aliases in `~/.gitconfig`.
3. Test initial fixed worktree setup with `gw-init capita` and verify project-scoped branching and commits.
