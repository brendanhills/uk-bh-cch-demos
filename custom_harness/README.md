# Custom Harness for Antigravity & Jetski

This repository directory provides a custom harness and agent extensions for **Antigravity** and **Jetski**.

## 🛠️ Included Components

### 1. Conductor Extension (Submodule)
- **Submodule Path**: `conductor/`
- **Source**: [https://github.com/gemini-cli-extensions/conductor](https://github.com/gemini-cli-extensions/conductor)
- Provides Spec-Driven Development commands: `/conductor:setup`, `/conductor:newTrack`, `/conductor:review`.

### 2. Bug Management Protocol & Slash Commands (`.agents/skills`)
- **`/bug`**: Log a bug report into `.agents/bugs.json` with empty priority/impact fields without fixing it immediately.
- **`/triage_bug [#id]`**: Investigate cause, plan solution, assign `priority` (`P0`–`P3`) and `impact` (`Critical`–`Low`), and update status to `"Investigated"`. Automatically skips closed bugs in batch mode.
- **`/list_bugs`**: Render a structured Markdown table of workspace bugs with scope filtering (`all`/`resolved`) and Priority-tier grouping (`P0` first).
- **`/fix_bug [#id]`**: Fix bugs using **Adaptive Tiered Verification** (Tier 1 fast-path, Tier 2 suite augmentation, Tier 3 reproduction tests) and a **2-Retry Circuit Breaker** against test-debugging loops.

### 3. Global Agent Rules (`.agents/rules`)
- **`zero_approval_spam_standards.md`**: Prohibits inline `python3 -c` / `bash -c` one-liners in terminal commands, mandating native read-tools or standalone scripts in `scratch/` to prevent UI approval prompt spam.
- **`cloudtop_git_velocity.md`**: Enforces atomic, compound Git execution (`git add ... && git commit ... && git push`) and forbids sequential diagnostic spam to prevent corporate SSH/FIDO2 latency stalls.
- **`pragmatic_testing_standards.md`**: Enforces Implementation-First Velocity (no default TDD in normal chat), the 3-Tier Test Execution Heuristics Matrix (skipping backend tests for Frontend UI/CSS styling), and the 2-Retry Test-Debugging Circuit Breaker.
- **`standalone_customization_architecture.md`**: Mandates symlink architecture for global extensions in Standalone Jetski and Antigravity.
- **`agent_safety_and_batch_standards.md`**: Prohibits agents from modifying system-protected global `AGENTS.md` files and defines Skipping vs. Halting standards for batch operations.

## 📦 Installation & Setup


Use the provided automated installer script [`install.sh`](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/custom_harness/install.sh):

### Global Installation (Default)
Installs all skills globally to `~/.gemini/config/skills/`:
```bash
./install.sh
```

### Local Workspace Installation
Installs skills locally into a specific project's `.agents/skills/` directory:
```bash
./install.sh --local /path/to/target/workspace
```

## 🚀 Usage

Once installed, access the interactive `/` slash commands directly in Jetski or Antigravity!

