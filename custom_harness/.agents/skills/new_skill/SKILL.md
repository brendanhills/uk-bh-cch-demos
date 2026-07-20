---
name: new_skill
description: Scaffold and create a new custom skill and slash command for Jetski and Antigravity.
---

# Create New Skill Command (`/new_skill`)

When the user runs `/new_skill`:

### 1. Extract Inputs
Extract the following details from the user's prompt or ask for them if missing:
- **`name`**: Skill / command name (lowercase, e.g. `code_review`, `verify_build`).
- **`description`**: A concise sentence describing what the skill does.
- **`scope`**: `global` (saves to `~/.gemini/config/skills/`) or `project` (saves to `<workspace-root>/.agents/skills/`). Default is `global`.

### 2. File Creation
Create the skill directory and `SKILL.md` file at `<target_directory>/<name>/SKILL.md` with YAML frontmatter:

```markdown
---
name: <name>
description: <description>
---

# <Name> Command (`/<name>`)

When the user runs `/<name>`:
1. <Step 1>
2. <Step 2>
```

### 3. Confirmation
Notify the user that the skill is created and ready for use via `/<name>`.
