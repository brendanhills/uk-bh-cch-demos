#!/usr/bin/env python3
"""
CLI Tool: Context Health & Prompt Caching Inspector
Generates a.
"""

import glob
import os

DEFAULT_CONTEXT_WINDOW_LIMIT = 1000000  # 1M.

def estimate_tokens(text: str) -> int:
    return len(text) // 4 if text else 0

def generate_markdown_report(workspace_dir):
    # Dynamically find all.
    rule_files = glob.glob(os.path.join(workspace_dir, "**", "rules", "*.md"), recursive=True)
    agents_md = os.path.join(workspace_dir, "AGENTS.md")
    if os.path.exists(agents_md) and agents_md not in rule_files:
        rule_files.append(agents_md)

    always_on_rules = []
    progressive_rules = []

    for rf in rule_files:
        rel_path = os.path.relpath(rf, workspace_dir)
        try:
            with open(rf, "r", encoding="utf-8") as f:
                content = f.read()
                tokens = estimate_tokens(content)
                item = {"file": rel_path, "tokens": tokens}
                if "trigger: model_decision" in content or "trigger: glob" in content:
                    progressive_rules.append(item)
                else:
                    always_on_rules.append(item)
        except Exception:
            pass

    always_on_tokens = sum(r["tokens"] for r in always_on_rules)
    progressive_rules_tokens = sum(r["tokens"] for r in progressive_rules)

    # Dynamically find all SKILL.md files.
    skill_files = glob.glob(os.path.join(workspace_dir, "**", "SKILL.md"), recursive=True)
    skill_items = []

    for sf in skill_files:
        rel_path = os.path.relpath(sf, workspace_dir)
        try:
            with open(sf, "r", encoding="utf-8") as f:
                content = f.read()
                tokens = estimate_tokens(content)
                skill_name = os.path.basename(os.path.dirname(sf))
                for line in content.splitlines():
                    if line.startswith("name:"):
                        skill_name = line.split(":", 1)[1].strip()
                        break
                skill_items.append({"name": skill_name, "file": rel_path, "tokens": tokens})
        except Exception:
            pass

    total_skill_tokens = sum(s["tokens"] for s in skill_items)
    
    heuristics_file = os.path.join(workspace_dir, ".agents", "prompt_heuristics.md")
    heuristics_tokens = 0
    if os.path.exists(heuristics_file):
        try:
            with open(heuristics_file, "r", encoding="utf-8") as f:
                heuristics_tokens = estimate_tokens(f.read())
        except Exception:
            pass

    total_static_tokens = always_on_tokens
    total_indexed_tokens = progressive_rules_tokens + total_skill_tokens + heuristics_tokens
    pct_limit_used = (total_static_tokens / DEFAULT_CONTEXT_WINDOW_LIMIT) * 100
    efficiency = 100.0 - pct_limit_used

    lines = []
    lines.append("# 📊 Context Health & Prompt Caching Report\n")
    lines.append("## Summary Metrics\n")
    lines.append("| Metric | Value | % of Context Limit |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **Max Context Window Limit** | {DEFAULT_CONTEXT_WINDOW_LIMIT:,} tokens | 100.0% |")
    lines.append(f"| **Always-On Static Load** | {total_static_tokens:,} tokens | {pct_limit_used:.3f}% |")
    lines.append(f"| **Progressive / On-Demand Index** | {total_indexed_tokens:,} tokens | {total_indexed_tokens / DEFAULT_CONTEXT_WINDOW_LIMIT * 100:.2f}% |\n")

    if always_on_rules:
        lines.append("| Rule File | Tokens | Status |")
        lines.append("| :--- | :--- | :--- |")
        for r in always_on_rules:
            lines.append(f"| `{r['file']}` | {r['tokens']:,} | Always Loaded |")
    else:
        lines.append("No always-on rules found.")

    lines.append("\n## 🧰 Dynamic Skills Breakdown (Progressive / On-Demand)\n")
    if skill_items:
        lines.append("| Skill Name | File Path | Tokens |")
        lines.append("| :--- | :--- | :--- |")
        for s in sorted(skill_items, key=lambda x: x['tokens'], reverse=True):
            lines.append(f"| `{s['name']}` | `{s['file']}` | {s['tokens']:,} |")
        lines.append(f"\n**Total Skills ({len(skill_items)} items)**: {total_skill_tokens:,} tokens\n")
    else:
        lines.append("No skills found.")

    lines.append("## ⚡ Prompt Caching & Context Efficiency\n")
    lines.append(f"- **Cached System Baseline**: {total_static_tokens:,} tokens (persisted across turns)")
    lines.append(f"- **Context Efficiency**: **{efficiency:.2f}% clean** (Only {total_static_tokens:,} tokens in baseline)")

    return "\n".join(lines)

def main():
    workspace = os.getcwd()
    print(generate_markdown_report(workspace))

if __name__ == "__main__":
    main()
