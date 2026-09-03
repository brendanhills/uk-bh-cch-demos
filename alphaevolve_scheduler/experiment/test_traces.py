import json
import unittest
from pathlib import Path
from experiment.config import load_config
from experiment.evaluator import evaluate_schedule, InfeasibilityError

ROOT = Path(__file__).resolve().parent.parent

class TestTraceGenerationAndKeying(unittest.TestCase):
    def setUp(self):
        self.config = load_config(str(ROOT / "data" / "config.json"))
        self.trace_files = ["traces_low.jsonl", "traces_dynamic.jsonl"]

    def test_trace_files_exist_and_parse(self):
        for fname in self.trace_files:
            tpath = ROOT / "data" / fname
            self.assertTrue(tpath.exists(), f"Trace file {fname} is missing")
            
            lines = [json.loads(l) for l in tpath.read_text().strip().split("\n") if l.strip()]
            self.assertGreaterEqual(len(lines), 2, f"{fname} should contain at least Step 0 and Step 1")
            
            step0, step1 = lines[0], lines[1]
            self.assertEqual(step0["step"], 0)
            self.assertEqual(step1["step"], 1)
            
            # Assert Throughput progression: Peak step >= Step 0
            max_scheduled = max(l["metrics"]["patientsScheduled"] for l in lines)
            self.assertGreaterEqual(
                max_scheduled,
                step0["metrics"]["patientsScheduled"],
                f"{fname}: Peak step throughput should meet or exceed Step 0"
            )

    def test_appointment_block_keys_and_fields(self):
        for fname in self.trace_files:
            tpath = ROOT / "data" / fname
            lines = [json.loads(l) for l in tpath.read_text().strip().split("\n") if l.strip()]
            
            for step_data in lines:
                schedules = step_data.get("schedules", [])
                self.assertGreater(len(schedules), 0, f"{fname} step {step_data['step']} has empty schedule")
                
                patient_ids = set()
                for appt in schedules:
                    pid = appt.get("patientId") or appt.get("demandId")
                    self.assertTrue(bool(pid), f"Missing patientId/demandId in {fname}")
                    self.assertIn("resourceId", appt, f"Missing resourceId in {fname}")
                    self.assertIn("startTime", appt, f"Missing startTime in {fname}")
                    self.assertIn("endTime", appt, f"Missing endTime in {fname}")
                    self.assertIn("day", appt, f"Missing day in {fname}")
                    patient_ids.add(pid)
                    
                # Assert patient/demand IDs are unique within the scheduled step
                self.assertEqual(len(patient_ids), len(schedules), f"Duplicate patientId/demandId in {fname}")

    def test_trace_evaluator_feasibility(self):
        for fname in self.trace_files:
            tpath = ROOT / "data" / fname
            lines = [json.loads(l) for l in tpath.read_text().strip().split("\n") if l.strip()]
            
            for step_data in lines:
                raw_schedules = step_data["schedules"]
                try:
                    res = evaluate_schedule(raw_schedules, self.config)
                    self.assertGreater(res["patientsScheduled"], 0)
                    self.assertIn("score", res)
                except InfeasibilityError as e:
                    self.fail(f"Feasibility evaluation failed for {fname} step {step_data['step']}: {e}")

    def test_dynamic_live_run_has_5_day_schedule(self):
        """Bug #13 verification: Ensure traces_dynamic schedule spans all 5 weekdays."""
        tpath = ROOT / "data" / "traces_dynamic.jsonl"
        if not tpath.exists():
            self.skipTest("traces_dynamic.jsonl does not exist yet")
        
        lines = [json.loads(l) for l in tpath.read_text().strip().split("\n") if l.strip()]
        for step_data in lines:
            schedules = step_data.get("schedules", [])
            days_scheduled = {appt.get("day") for appt in schedules}
            expected_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
            self.assertTrue(
                expected_days.issubset(days_scheduled), 
                f"Step {step_data.get('step')} only schedules on {days_scheduled}, expected all 5 days {expected_days}"
            )

if __name__ == "__main__":
    unittest.main()
