import os
import unittest
from unittest.mock import patch
from pathlib import Path
import json

# Set root
ROOT = Path(__file__).resolve().parent.parent

# Set dummy env before importing run_evolution
os.environ["PROJECT_ID"] = "dummy-project"
os.environ["GE_APP_ID"] = "dummy-app"
os.environ["TRACE_FILENAME"] = "test_reproduce_bug1_traces.jsonl"

from experiment.run_evolution import main

class TestReproduceBug1(unittest.TestCase):
    def setUp(self):
        self.trace_file = ROOT / "data" / "test_reproduce_bug1_traces.jsonl"
        # Pre-create the file to simulate it existing from a previous run
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.trace_file, "w") as f:
            f.write("dummy previous run data\n")

    def tearDown(self):
        if self.trace_file.exists():
            self.trace_file.unlink()

    @patch("experiment.run_evolution.run_controller_loop")
    @patch("experiment.run_evolution.AlphaEvolveExperiment")
    def test_trace_file_exists_immediately(self, mock_experiment_class, mock_loop):
        mock_experiment = mock_experiment_class.return_value
        
        # Define side_effect to enforce sequence check
        def assert_file_exists_before_session(*args, **kwargs):
            self.assertTrue(self.trace_file.exists(), "Trace file does not exist when create_experiment is called!")
            with open(self.trace_file) as f:
                lines = f.readlines()
            self.assertTrue(len(lines) > 0, "Trace file is empty when create_experiment is called!")
            first_step = json.loads(lines[0])
            self.assertEqual(first_step["step"], 0, "Step 0 was not written before create_experiment was called!")
            
        mock_experiment.create_experiment.side_effect = assert_file_exists_before_session
        
        # Run main setup
        try:
            main()
        except SystemExit:
            pass # Handle any sys.exit in case setup fails
        
        # Verify the file is NOT missing on disk
        self.assertTrue(self.trace_file.exists(), "Trace file was deleted and not recreated on startup!")
        
        # Verify that it contains at least Step 0 (the baseline)
        with open(self.trace_file) as f:
            lines = f.readlines()
        self.assertTrue(len(lines) > 0, "Trace file is empty on startup!")
        first_step = json.loads(lines[0])
        self.assertEqual(first_step["step"], 0, "First step in trace file is not Step 0 (Baseline)!")

if __name__ == "__main__":
    unittest.main()
