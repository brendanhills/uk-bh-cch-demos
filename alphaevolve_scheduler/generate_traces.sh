#!/usr/bin/env bash
# Change directory to the script's own folder to ensure local execution
cd "$(dirname "$0")"

# Sequential pre-computation of our 3 Operational Scenarios
exec > generate.log 2>&1
echo "Starting Sequential Scenario Pre-Computation (ETA ~6-8 mins)..."
SCENARIO=agile TRACE_FILENAME=traces_low.jsonl uv run python -u experiment/run_evolution.py
SCENARIO=standard TRACE_FILENAME=traces_med.jsonl uv run python -u experiment/run_evolution.py
SCENARIO=legacy TRACE_FILENAME=traces_high.jsonl uv run python -u experiment/run_evolution.py
echo "All Scenarios Successfully Generated! 🎉"
