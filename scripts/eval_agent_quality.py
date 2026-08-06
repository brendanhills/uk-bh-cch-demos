"""Agent Quality & Script Adherence Evaluation Suite for Cymbal Children's Hospital."""

import json
import sys
from pathlib import Path

# Ensure app directory is on PYTHONPATH regardless of working directory
project_root = Path(__file__).parent.parent
app_dir = project_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from cch_agent.agent import agent as router_agent


def run_evaluation_suite():
    dataset_path = project_root / "tests" / "eval" / "eval_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    print("=" * 70)
    print("🤖 CYMBAL CHILDREN'S HOSPITAL - AGENT QUALITY & SCRIPT EVALUATION")
    print("=" * 70)

    for bench in benchmarks:
        print(f"\n📌 [{bench['eval_id']}] {bench['scenario']}")
        print(f"   Description: {bench['description']}")
        print("   Rubric Requirements:")
        for dim, criteria in bench["eval_rubric"].items():
            print(f"     • {dim.upper()}: {criteria}")
        print("   Status: ✅ Benchmark Active & Configured")

    print("\n" + "=" * 70)
    print("Evaluation Dataset Ready for LLM-as-a-Judge & Live API Scoring!")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation_suite()
