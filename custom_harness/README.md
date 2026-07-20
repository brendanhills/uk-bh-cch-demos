# Custom Harness for Antigravity & Jetski

This repository directory provides a custom harness and agent extensions for **Antigravity** and **Jetski**.

## 🛠️ Included Components

### 1. Conductor Extension (Submodule)
- **Submodule Path**: `conductor/`
- **Source**: [https://github.com/gemini-cli-extensions/conductor](https://github.com/gemini-cli-extensions/conductor)
- Provides Spec-Driven Development commands: `/conductor:setup`, `/conductor:newTrack`, `/conductor:review`.

### 2. Bug Management Protocol & Slash Commands (`.agents/skills`)
- **`/bug`**: Log a bug report into `.agents/bugs.json` without fixing it immediately.
- **`/triage_bug [#id]`**: Investigate cause, plan solution, assign `priority` (`P0`–`P3`) and `impact` (`Critical`–`Low`), and update status to `"Investigated"` without fixing.
- **`/list_bugs`**: Render a structured Markdown table of all recorded workspace bugs.
- **`/fix_bug [#id]`**: Write an automated reproduction unit test first, implement fix, and update status upon passing tests.

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

