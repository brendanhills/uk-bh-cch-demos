#!/usr/bin/env python3
"""
CLI Tool: Prompt Heuristics Metrics Aggregator
Reads .agents/prompt_heuristics_log.jsonl and displays trigger statistics.
"""

from collections import Counter
import json
import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = os.path.dirname(script_dir)
    log_file_path = os.path.join(agents_dir, "prompt_heuristics_log.jsonl")

    if not os.path.exists(log_file_path):
        print("No prompt heuristics trigger logs found yet.")
        return

    rule_counts = Counter()
    total_events = 0

    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    total_events += 1
                    data = json.loads(line)
                    for rule in data.get("triggered_rules", []):
                        rule_counts[rule] += 1
    except Exception as e:
        print(f"Error reading metrics log: {e}")
        return

    print("=== Prompt Heuristics Trigger Metrics ===")
    print(f"Total Trigger Events: {total_events}\n")
    print(f"{'Rule Name':<30} | {'Trigger Count':<13}")
    print("-" * 46)

    for rule, count in rule_counts.most_common():
        print(f"{rule:<30} | {count:<13}")

if __name__ == "__main__":
    main()
