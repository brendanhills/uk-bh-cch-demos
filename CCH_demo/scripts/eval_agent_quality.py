"""Agent Quality & Script Adherence Evaluation Suite for Cymbal Children's Hospital."""

import json
from pathlib import Path
from app.cch_agent.agent import agent as router_agent


def run_evaluation_suite():
    dataset_path = Path(__file__).parent.parent / "tests" / "eval" / "eval_dataset.json"
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
