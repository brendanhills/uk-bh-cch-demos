#!/usr/bin/env python3
"""
PreInvocation Hook Script: Smart Prompt Heuristics Evaluator (Option B) with Metrics Tracking
Intercepts user prompts, pre-screens them against heuristics,
injects feedback when underspecified, and logs trigger metrics.
"""

from datetime import datetime, timezone
import json
import os
import re
import sys

# Commands, questions, and short responses to bypass screening
BYPASS_PATTERNS = [
    r"^/.*",  # Slash commands
    r"^(yes|no|y|n|ok|okay|proceed|continue|b|a|c|d|checkpoint|cancel)$",
    r"^\s*(what|where|how|why|show|explain|list|tell|status|check|review|summarize)\b.*",  # Question /5.  informational
]

# Action verbs paired with.
VAGUE_ACTION_REGEX = re.compile(
    r"\b(fix|change|update|refactor|delete|modify|debug|edit|do)\s+(this|that|it)\b"
    r"|\b(make)\s+it\s+(work|pass|build|run|better)\b",
    re.IGNORECASE
)

FILE_EXTENSION_REGEX = re.compile(r"\b\w+\.(py|ts|tsx|js|jsx|cc|cpp|h|go|java|json|md|yaml|yml|sh)\b", re.IGNORECASE)
BROAD_SCOPE_REGEX = re.compile(r"\b(migrate the whole|refactor everything|fix all|rewrite the app|add tests for everything)\b", re.IGNORECASE)

def should_bypass(prompt: str) -> bool:
    prompt_strip = prompt.strip().lower()
    if not prompt_strip:
        return True
    for pat in BYPASS_PATTERNS:
        if re.search(pat, prompt_strip):
            return True
    return False

def evaluate_prompt(prompt: str) -> dict:
    triggered = {}
    
    # Check 1: Action verb + vague pronoun without file context (Remove Ambiguity)
    if VAGUE_ACTION_REGEX.search(prompt) and not FILE_EXTENSION_REGEX.search(prompt):
        triggered["Remove Ambiguity"] = "- **Remove Ambiguity**: Prompt asks to modify/fix 'this', 'that', or 'it' without specifying the target file, function, or line range."

    # Check 2: Broad, un-scoped overhaul (Decompose)
    if BROAD_SCOPE_REGEX.search(prompt):
        triggered["Decompose"] = "- **Decompose**: Prompt requests a broad application-wide overhaul. Consider0.  scoping to Step 1."

    # Check 3: Extremely short command with action verb
    words = prompt.split()
    if len(words) <= 3 and not FILE_EXTENSION_REGEX.search(prompt) and any(w.lower() in ["fix", "add", "change", "update", "create", "test", "build"] for w in words):
        triggered["Be Specific"] = "- **Be Specific**: Short command detected. Name the specific file(s), test cases, and tools to use."

    return triggered

def log_trigger_metrics(log_file_path: str, conversation_id: str, prompt: str, triggered_rules: list):
    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conversation_id": conversation_id,
            "triggered_rules": triggered_rules,
            "prompt_snippet": prompt[:100]  # First 100 chars
        }
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception:
        pass

def main():
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    transcript_path = input_data.get("transcriptPath")
    conversation_id = input_data.get("conversationId", "unknown")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(script_dir)
    log_file_path = os.path.join(agents_dir, "prompt_heuristics_log.jsonl")

    last_user_prompt = ""
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        if entry.get("type") == "USER_INPUT":
                            last_user_prompt = entry.get("content", "")
        except Exception:
            pass

    output = {"injectSteps": []}

    if last_user_prompt and not should_bypass(last_user_prompt):
        triggered_dict = evaluate_prompt(last_user_prompt)
        if triggered_dict:
            triggered_rules = list(triggered_dict.keys())
            log_trigger_metrics(log_file_path, conversation_id, last_user_prompt, triggered_rules)
            
            heuristics_summary = "\n".join(triggered_dict.values())
            ephemeral_msg = (
                "SYSTEM DIRECTIVE - PROMPT HEURISTICS AUDIT:\n"
                "The user's prompt appears underspecified:\n"
                f"{heuristics_summary}\n\n"
                "INSTRUCTIONS:\n"
                "1. Briefly explain which heuristic was triggered.\n"
                "2. Provide a COMPLETE, fully-written example of a well-formed prompt.\n"
                "3. Ask if the user wants to refine their prompt or proceed."
            )
            output["injectSteps"].append({"ephemeralMessage": ephemeral_msg})

    print(json.dumps(output))

if __name__ == "__main__":
    main()
