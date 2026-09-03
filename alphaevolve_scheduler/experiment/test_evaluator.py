import unittest
from pathlib import Path
from experiment.config import load_config
from experiment.evaluator import evaluate_schedule, InfeasibilityError

ROOT = Path(__file__).resolve().parent.parent

class TestEvaluator(unittest.TestCase):
    def setUp(self):
        self.config = load_config(str(ROOT / "data" / "config.json"))

    def test_empty_schedule_evaluation(self):
        metrics = evaluate_schedule([], self.config)
        self.assertIn("score", metrics)
        self.assertEqual(metrics["patientsScheduled"], 0)

    def test_invalid_demand_rejection(self):
        bad_schedule = [{
            "id": "A_BAD",
            "demandId": "NON_EXISTENT_DEMAND",
            "resourceId": self.config.resources[0].id,
            "startTime": "08:00",
            "endTime": "09:00",
            "day": "Monday",
            "staffIds": []
        }]
        with self.assertRaises(InfeasibilityError):
            evaluate_schedule(bad_schedule, self.config)

    def test_resource_overlap_rejection(self):
        r_id = self.config.resources[0].id
        d1 = self.config.demands[0]
        d2 = self.config.demands[1]
        
        overlapping_schedule = [
            {
                "id": "A1",
                "demandId": d1.id,
                "resourceId": r_id,
                "startTime": "08:00",
                "endTime": "10:00",
                "day": "Monday",
                "staffIds": []
            },
            {
                "id": "A2",
                "demandId": d2.id,
                "resourceId": r_id,
                "startTime": "09:00",
                "endTime": "11:00",
                "day": "Monday",
                "staffIds": []
            }
        ]
        with self.assertRaises(InfeasibilityError):
            evaluate_schedule(overlapping_schedule, self.config)

    def test_bugs7_and_9_resource_idle_time_non_zero(self):
        """Bugs #7 & #9: Ensure evaluate_schedule computes accurate non-zero idle time across 5-day horizon."""
        d1 = self.config.demands[0]
        r_id = self.config.resources[0].id
        
        # Schedule only 1 surgery (2 hours) across 5 days (18,000 gross room minutes)
        single_appt = [{
            "id": "A1",
            "demandId": d1.id,
            "resourceId": r_id,
            "startTime": "08:00",
            "endTime": "11:15",
            "day": "Monday",
            "staffIds": [s.id for s in self.config.staff if any(role in s.skills for role in d1.required_roles)]
        }]
        metrics = evaluate_schedule(single_appt, self.config)
        self.assertGreater(metrics["resourceIdleTime"], 0, "resourceIdleTime should be non-zero when schedule has unused room gaps")
        expected_idle = (5 * len(self.config.resources) * 12 * 60) - d1.duration_minutes
        self.assertEqual(metrics["resourceIdleTime"], expected_idle)

if __name__ == "__main__":
    unittest.main()

