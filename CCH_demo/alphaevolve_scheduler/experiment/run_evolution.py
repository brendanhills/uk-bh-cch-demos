import asyncio
import json
import logging
import os
import sys
import threading
import time
from pathlib import Path

import nest_asyncio
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiment"))

from alpha_evolve.client import AlphaEvolveClient
from alpha_evolve.controller import run_controller_loop
from alpha_evolve.experiment import AlphaEvolveExperiment

from config import load_config
from evaluator import safe_evaluate, FAIL_SCORE

logger = logging.getLogger("rch-run")

METRIC = "score"
SEED_SOURCE = (ROOT / "experiment" / "program.py").read_text()
INSTRUCTIONS = (ROOT / "experiment" / "instructions.md").read_text()

_lock = threading.Lock()
_counter = {
    "step": 0,
    "total_candidates": 0,
    "accepted_candidates": 0,
    "infeasible_candidates": 0,
}

config = load_config()
demands_map = {d.id: d for d in config.demands}


def stream_trace(metrics: dict, schedules: list, code: str, insight_title: str = None, insight_summary: str = None):
    """Formats and appends a successful candidate snapshot to traces.jsonl.
    
    Args:
        metrics: Dictionary containing evaluator score and constraints.
        schedules: List of appointment dicts for Gantt mapping.
        code: Evolved Python string for the UI transparent panel.
    """
    with _lock:
        step = _counter["step"]
        _counter["step"] += 1
        
        enriched_schedules = []
        for appt in schedules:
            demand = demands_map.get(appt.get("demandId"))
            patient_id = appt.get("patientId") or (demand.patient_id if demand else appt.get("demandId") or appt.get("id"))
            priority = appt.get("priority", getattr(demand, "priority", 2) if demand else 2)
            day = appt.get("day", "Monday")

            enriched_appt = {
                "id": appt["id"],
                "patientId": patient_id,
                "resourceId": appt["resourceId"],
                "day": day,
                "startTime": appt["startTime"],
                "endTime": appt["endTime"],
                "staffIds": appt["staffIds"],
                "priority": priority
            }
            for key in ("orig_day", "orig_room", "orig_time", "orig_staff", "prev_day", "prev_room", "prev_time", "prev_staff", "mutation_reason"):
                if key in appt:
                    enriched_appt[key] = appt[key]
            enriched_schedules.append(enriched_appt)
            
        insight = {
            "id": f"Cand_{step}",
            "generation": step,
            "title": insight_title or ("Baseline FCFS Heuristic" if step == 0 else f"AlphaEvolve Mutated Heuristic #{step}"),
            "status": "BASELINE" if step == 0 else "ACCEPTED",
            "score": metrics.get("score", 0.0),
            "metrics": {
                "patientsScheduled": metrics["patientsScheduled"],
                "overtimeHours": metrics["overtimeHours"],
                "resourceIdleTime": metrics["resourceIdleTime"],
                "fatigueViolations": metrics["fatigueViolations"],
            },
            "summary": insight_summary or (
                "Naive First-Come-First-Served greedy assignment. Leaves fragmented time gaps and unmanaged rest intervals." if step == 0
                else f"AlphaEvolve generated a mutated Python schedule optimizer, increasing patient throughput to {metrics['patientsScheduled']} while balancing fatigue rules."
            ),
            "code": code,
            "timestamp": time.strftime("%H:%M:%S")
        }

        entry = {
            "step": step,
            "metrics": {
                "patientsScheduled": metrics["patientsScheduled"],
                "overtimeHours": metrics["overtimeHours"],
                "resourceIdleTime": metrics["resourceIdleTime"],
                "fatigueViolations": metrics["fatigueViolations"],
                "totalCandidatesEvaluated": _counter["total_candidates"],
                "acceptedCount": _counter["accepted_candidates"],
                "infeasibleCount": _counter["infeasible_candidates"],
            },
            "schedules": enriched_schedules,
            "code": code,
            "insight": insight
        }
        
        trace_path = (
            ROOT / "data" / os.environ.get("TRACE_FILENAME", "traces.jsonl")
        )
        with trace_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
        feed_path = ROOT / "data" / "candidates_feed.jsonl"
        with feed_path.open("a") as f:
            f.write(json.dumps(insight) + "\n")
            f.flush()

        color = "🟢"
        print(f"\n[{step*3}s] {color} CANDIDATE #{step}: {insight['title']} [{insight['status']}]")
        print(f"      Score: {insight['score']:,.1f} | Patients Scheduled: {metrics['patientsScheduled']} | Idle: {metrics['resourceIdleTime']}m | Overtime: {metrics['overtimeHours']}h | Fatigue Violations: {metrics['fatigueViolations']}")
        print(f"      💡 Insight: {insight['summary']}")
            
        logger.info(
            f"Streamed Candidate #{step}: "
            f"Score {metrics['score']:.1f}, "
            f"Patients: {metrics['patientsScheduled']}, "
            f"Idle: {metrics['resourceIdleTime']}m"
        )


def rch_evaluation_function(program_candidate: dict) -> dict:
    """Evaluates a program candidate and streams successful traces to the UI.
    
    Args:
        program_candidate: AlphaEvolve dictionary payload containing files.
        
    Returns:
        A dictionary mapping the objective score to the AlphaEvolve engine.
    """
    code = program_candidate["content"]["files"][0]["content"]
    
    with _lock:
        _counter["total_candidates"] += 1
        
    result = safe_evaluate(code, config)
    score = result["score"]
    
    if score == FAIL_SCORE:
        with _lock:
            _counter["infeasible_candidates"] += 1
            step = _counter["step"]
            _counter["step"] += 1
        name = program_candidate.get("name", "unknown")
        error_reason = result.get("error", "Invalid schedule or syntax error.")
        logger.info(f"Candidate {name} rejected: {error_reason}")
        
        insight = {
            "id": f"Cand_{step}",
            "generation": step,
            "title": f"AlphaEvolve Mutated Candidate #{step}",
            "status": "REJECTED",
            "score": FAIL_SCORE,
            "metrics": {
                "patientsScheduled": 0,
                "overtimeHours": 0.0,
                "resourceIdleTime": 0,
                "fatigueViolations": 0,
            },
            "summary": f"AlphaEvolve recorded an execution error ({error_reason}) and rejected this mutation.",
            "code": code,
            "timestamp": time.strftime("%H:%M:%S")
        }
        try:
            feed_path = ROOT / "data" / "candidates_feed.jsonl"
            with feed_path.open("a") as f:
                f.write(json.dumps(insight) + "\n")
                f.flush()
        except Exception:
            pass

        color = "🔴"
        print(f"\n[{step*3}s] {color} CANDIDATE #{step}: {insight['title']} [{insight['status']}]")
        print(f"      Score: {FAIL_SCORE} | Patients Scheduled: 0 | Idle: 0m | Overtime: 0.0h | Fatigue Violations: 0")
        print(f"      💡 Insight: {insight['summary']}")

        return {
            "scores": {"scores": [{"metric": METRIC, "score": FAIL_SCORE}]}
        }
        
    with _lock:
        _counter["accepted_candidates"] += 1
        
    stream_trace(result["metrics"], result["schedules"], code)
    
    return {"scores": {"scores": [{"metric": METRIC, "score": score}]}}


def main():
    """Main execution loop initializing and launching the evolutionary engine."""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)-7s %(name)s %(message)s")
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("alpha_evolve.client").setLevel(logging.WARNING)
    logging.getLogger("alpha_evolve.workers").setLevel(logging.INFO)
                        
    load_dotenv(ROOT / "experiment" / ".env")
    
    trace_name = os.environ.get("TRACE_FILENAME", "traces.jsonl")
    trace_jsonl = ROOT / "data" / trace_name
    
    if trace_jsonl.exists():
        trace_jsonl.unlink()
    trace_jsonl.parent.mkdir(parents=True, exist_ok=True)

    feed_jsonl = ROOT / "data" / "candidates_feed.jsonl"
    if feed_jsonl.exists():
        feed_jsonl.unlink()
    
    seed_eval = safe_evaluate(SEED_SOURCE, config)
    if seed_eval["score"] == FAIL_SCORE:
        logger.error(f"Seed program is invalid! Error: {seed_eval.get('error')}")
        sys.exit(1)
        
    logger.info("Seed evaluation successful. Streaming Baseline (Candidate #0)...")
    stream_trace(seed_eval["metrics"], seed_eval["schedules"], SEED_SOURCE)
    
    if not os.environ.get("PROJECT_ID") or not os.environ.get("GE_APP_ID"):
        logger.error("Missing PROJECT_ID or GE_APP_ID in experiment/.env!")
        sys.exit(1)
        
    client = AlphaEvolveClient(
        project_id=os.environ["PROJECT_ID"],
        location=os.getenv("LOCATION", "global"),
        collection=os.getenv("COLLECTION", "default_collection"),
        engine=os.environ["GE_APP_ID"],
    )
    
    experiment = AlphaEvolveExperiment(
        ae_client=client,
        evaluator_function=rch_evaluation_function,
        max_programs_evaluated=int(
            os.getenv("MAX_PROGRAMS_EVALUATED", "10")
        ),
        parallel_evaluation=False,
    )
    
    experiment.create_experiment({
        "title": "CCH Hospital Co-Scheduling Optimization",
        "problem_description": INSTRUCTIONS,
        "program_language": "python",
        "run_settings": {
            "max_programs": int(os.getenv("MAX_PROGRAMS_GENERATED", "15")),
            "concurrency": int(os.getenv("CONCURRENCY", "4")),
        },
        "generation_settings": {
            "models": [{"name": os.getenv("MODEL", "gemini-3.5-flash")}]
        },
    })
    
    experiment.create_initial_program({
        "content": {"files": [{"path": "main.py", "content": SEED_SOURCE}]},
        "evaluation": {"scores": {"scores": [{"metric": METRIC, "score": seed_eval["score"]}]}},
    })
    
    experiment.start_experiment()
    logger.info("Experiment started: %s", experiment.experiment_name)
    
    nest_asyncio.apply()
    idle_timeout = int(os.getenv("IDLE_TIMEOUT", "300"))
    asyncio.run(run_controller_loop(experiment, idle_timeout_s=idle_timeout))
    
    logger.info("Evolution complete! Real-time traces written to data/traces.jsonl")

if __name__ == "__main__":
    main()
