#!/usr/bin/env python3
"""
CLI Tool: Progressive Disclosure Auditor
Scans.
"""

import os
import glob

def audit_rules(workspace_dir):
    rules = []
    rules_dir = os.path.join(workspace_dir, ".agents", "rules")
    conductor_rules_dir = os.path.join(workspace_dir, "conductor", "rules")
    
    files = glob.glob(os.path.join(rules_dir, "**", "*.md"), recursive=True) + \
            glob.glob(os.path.join(conductor_rules_dir, "**", "*.md"), recursive=True)
            
    agents_md = os.path.join(workspace_dir, "AGENTS.md")
    if os.path.exists(agents_md):
        files.append(agents_md)

    for file_path in files:
        rel_path = os.path.relpath(file_path, workspace_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            trigger = "always_on"
            if "trigger: model_decision" in content:
                trigger = "model_decision"
            elif "trigger: glob" in content:
                trigger = "glob"

            rules.append({
                "file": rel_path,
                "trigger": trigger,
                "size_bytes": len(content.encode('utf-8')),
                "approx_tokens": len(content) // 4
            })
        except Exception as e:
            rules.append({"file": rel_path, "error": str(e)})

    return rules

def audit_skills(workspace_dir):
    skills = []
    agents_skills = glob.glob(os.path.join(workspace_dir, ".agents", "skills", "**", "SKILL.md"), recursive=True)
    conductor_skills = glob.glob(os.path.join(workspace_dir, "conductor", "skills", "**", "SKILL.md"), recursive=True)
    skill_files = agents_skills + conductor_skills

    for file_path in skill_files:
        rel_path = os.path.relpath(file_path, workspace_dir)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            has_name = "name:" in content
            has_desc = "description:" in content
            skills.append({
                "file": rel_path,
                "valid_frontmatter": has_name and has_desc,
                "size_bytes": len(content.encode('utf-8')),
                "approx_tokens": len(content) // 4
            })
        except Exception as e:
            skills.append({"file": rel_path, "error": str(e)})

    return skills

def main():
    workspace = os.getcwd()
    print("=== Progressive Disclosure Audit Report ===")
    print(f"Workspace: {workspace}\n")

    rules = audit_rules(workspace)
    print("--- Rules Audit ---")
    always_on_count = 0
    model_decision_count = 0
    
    for r in rules:
        trigger = r.get("trigger", "unknown")
        if trigger == "always_on":
            always_on_count += 1
            status = "ALWAYS_ON"
        else:
            model_decision_count += 1
            status = "PROGRESSIVE"
        print(f"  [{status}] {r['file']} (~{r.get('approx_tokens', 0)} tokens)")

    print(f"\nRules Summary: {always_on_count} Always-On | {model_decision_count} Progressive\n")

    skills = audit_skills(workspace)
    print("--- Skills Audit ---")
    valid_skills = 0
    for s in skills:
        valid = s.get("valid_frontmatter", False)
        status = "VALID" if valid else "MISSING METADATA"
        if valid:
            valid_skills += 1
        print(f"  [{status}] {s['file']} (~{s.get('approx_tokens', 0)} tokens)")

    print(f"\nSkills Summary: {len(skills)} Total ({valid_skills} configured for progressive disclosure)")

if __name__ == "__main__":
    main()
