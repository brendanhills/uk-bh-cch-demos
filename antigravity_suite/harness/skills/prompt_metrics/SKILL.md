---
name: prompt_metrics
description: Display summary statistics and trigger metrics for prompt heuristics rules.
---

# Prompt Metrics Skill

Use this skill whenever the user asks to view prompt heuristics trigger metrics or stats.

### Execution Instructions:
Run the metrics aggregator script to display statistics on how often each rule has been triggered:

```bash
python3 .agents/scripts/prompt_metrics.py
```

Render the output cleanly in a markdown table for the user.
