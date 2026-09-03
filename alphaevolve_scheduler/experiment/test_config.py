import unittest
from pathlib import Path
from experiment.config import load_config, Config
from experiment.models import TimeSlot, Schedule, Appointment, Resource, Staff, Patient

ROOT = Path(__file__).resolve().parent.parent

class TestConfigAndModels(unittest.TestCase):
    def test_load_default_config(self):
        config_path = ROOT / "data" / "config.json"
        self.assertTrue(config_path.exists(), "data/config.json missing")
        cfg = load_config(str(config_path))
        self.assertIsInstance(cfg, Config)
        self.assertGreater(len(cfg.resources), 0)
        self.assertGreater(len(cfg.staff), 0)
        self.assertGreater(len(cfg.patients), 0)
        self.assertGreater(len(cfg.demands), 0)

    def test_timeslot_overlap(self):
        t1 = TimeSlot.from_str("08:00", "12:00", day="Monday")
        t2 = TimeSlot.from_str("10:00", "14:00", day="Monday")
        t3 = TimeSlot.from_str("12:00", "16:00", day="Monday")
        
        self.assertTrue(t1.overlaps(t2))
        self.assertFalse(t1.overlaps(t3))
        self.assertEqual(t1.duration, 240)

    def test_schedule_rest_violations(self):
        s = Staff(id="S1", name="Dr. Smith", role="Surgeon", skills={"Surgeon"})
        r = Resource(id="R1", name="Room 1", type="OT")
        p = Patient(id="P1", name="Patient 1", priority=1)
        
        t1 = TimeSlot.from_str("08:00", "12:00", day="Monday")
        t2 = TimeSlot.from_str("12:30", "17:00", day="Monday")  # Total 8.5h > 8h = 1 violation
        
        sched = Schedule()
        sched.add_appointment(Appointment("A1", p, r, t1, [s]))
        sched.add_appointment(Appointment("A2", p, r, t2, [s]))
        
        self.assertEqual(sched.get_staff_rest_violations("S1", min_rest_minutes=600), 1)

if __name__ == "__main__":
    unittest.main()
