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

## 🚀 Usage

To use this harness in any project:
1. Copy or symlink `.agents/skills` to your project's `.agents/skills/` or `~/.gemini/config/skills/`.
2. Access the interactive `/` commands directly in Jetski or Antigravity!
