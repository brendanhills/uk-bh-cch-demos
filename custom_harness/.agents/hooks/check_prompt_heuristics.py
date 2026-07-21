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

# Commands/short responses to bypass screening
BYPASS_PATTERNS = [
    r"^/.*",  # Slash commands
    r"^(yes|no|y|n|ok|okay|proceed|continue|b|a|c|d|checkpoint|cancel)$",
]

# Patterns indicating potential heuristic violations
VAGUE_PRONOUNS_REGEX = re.compile(r"\b(this|that|the other one|it)\b", re.IGNORECASE)
FILE_EXTENSION_REGEX = re.compile(r"\b\w+\.(py|ts|tsx|js|jsx|cc|cpp|h|go|java|json|md|yaml|yml|sh)\b", re.IGNORECASE)
BROAD_SCOPE_REGEX = re.compile(r"\b(migrate the whole|refactor everything|fix all|rewrite the app|add tests for everything)\b", re.IGNORECASE)

def should_bypass(prompt: str) -> bool:
    prompt_strip = prompt.strip().lower()
    if not prompt_strip:
        return True
    for pat in BYPASS_PATTERNS:
        if re.match(pat, prompt_strip):
            return True
    return False

def evaluate_prompt(prompt: str) -> dict:
    triggered = {}
    
    # Check 1: Vague pronouns without file context (Remove Ambiguity)
    if VAGUE_PRONOUNS_REGEX.search(prompt) and not FILE_EXTENSION_REGEX.search(prompt):
        triggered["Remove Ambiguity"] = "- **Remove Ambiguity**: Prompt uses vague pronouns ('this', 'that', 'it') without specifying exact filenames or line ranges."

    # Check 2: Broad application-wide overhaul without scoping (Decompose)
    if BROAD_SCOPE_REGEX.search(prompt):
        triggered["Decompose"] = "- **Decompose**: Prompt requests a broad application-wide overhaul. Consider scoping to Step 1 only."

    # Check 3: Short imperative request without file/tool specificity (Be Specific)
    words = prompt.split()
    if len(words) < 8 and not FILE_EXTENSION_REGEX.search(prompt) and any(w.lower() in ["fix", "add", "change", "update", "create", "test", "build"] for w in words):
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
    
    # Locate paths relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(script_dir)
    log_file_path = os.path.join(agents_dir, "prompt_heuristics_log.jsonl")

    # Read last user prompt from transcript
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

    # Evaluate prompt if not a bypass word
    if last_user_prompt and not should_bypass(last_user_prompt):
        triggered_dict = evaluate_prompt(last_user_prompt)
        if triggered_dict:
            triggered_rules = list(triggered_dict.keys())
            
            # Log metrics
            log_trigger_metrics(log_file_path, conversation_id, last_user_prompt, triggered_rules)
            
            # Build ephemeral advice message
            heuristics_summary = "\n".join(triggered_dict.values())
            ephemeral_msg = (
                "PROMPT HEURISTICS AUDIT (Smart Screening):\n"
                "The user's prompt may be underspecified according to the prompt heuristics guidelines:\n"
                f"{heuristics_summary}\n\n"
                "Gently highlight how the prompt could be made more specific or clear (citing the relevant heuristic), "
                "and ask if they want to refine it or proceed as is."
            )
            output["injectSteps"].append({"ephemeralMessage": ephemeral_msg})

    print(json.dumps(output))

if __name__ == "__main__":
    main()
