---
name: check_prompt
description: Audit and refine user prompts against stored prompt heuristics rules, or display trigger metrics.
---

# Check Prompt Skill

Use this skill to audit prompt drafts against prompt heuristics guidelines or view prompt improvement metrics.

### Usage:
1. **Audit a Prompt Draft**: Evaluate a draft prompt against all 9 prompt heuristics rules in `.agents/prompt_heuristics.md` and provide a refined version.
2. **View Metrics**: Run `.agents/scripts/prompt_metrics.py` to view statistics on how often each rule has been triggered across sessions.
