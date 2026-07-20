---
name: new_skill
description: Scaffold and create a new custom skill and slash command through interactive chat and design refinement.
---

# Create New Skill Command (`/new_skill`)

When the user runs `/new_skill` (with or without arguments):

### 1. Collaborative Chat & Idea Refinement
Do not require the user to specify name or description upfront. Instead, engage in a brief interactive chat:
- **Understand Goal**: Ask or clarify what the user wants the command to achieve.
- **Propose Name & Description**: Suggest an intuitive command `name` (lowercase, e.g. `review_tests`) and concise `description`.
- **Suggest Improvements**: Offer concrete enhancements to the workflow, such as edge cases, clear output formatting, or tool integrations.

### 2. Confirm Scope
Default to `global` (`~/.gemini/config/skills/`) so the command is available everywhere on the user's machine. Mention that `project` scope (`<workspace-root>/.agents/skills/`) is also available for repo sharing.

### 3. File Creation & Registration
Once aligned with the user, create `<target_directory>/<name>/SKILL.md` with YAML frontmatter:

```markdown
---
name: <name>
description: <description>
---

# <Name> Command (`/<name>`)

When the user runs `/<name>`:
1. <Refined Step 1>
2. <Refined Step 2>
```

Inform the user that the skill has been created and is immediately registered as `/<name>`.
