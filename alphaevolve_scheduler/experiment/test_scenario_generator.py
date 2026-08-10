import unittest
from generate_scenario import generate
from experiment.config import load_config
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestScenarioGenerator(unittest.TestCase):
    def test_scenario_generation_and_validation(self):
        generate()
        config_path = ROOT / "data" / "config.json"
        self.assertTrue(config_path.exists())
        
        cfg = load_config(str(config_path))
        self.assertEqual(len(cfg.resources), 5)
        self.assertEqual(len(cfg.staff), 16)
        self.assertEqual(len(cfg.patients), 160)
        self.assertEqual(len(cfg.demands), 160)

if __name__ == "__main__":
    unittest.main()
