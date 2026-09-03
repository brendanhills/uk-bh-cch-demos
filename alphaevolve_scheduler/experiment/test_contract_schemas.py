import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestContractSchemas(unittest.TestCase):
    def test_schema_files_exist_and_valid_json(self):
        """Verifies config and trace schema files exist and are valid JSON."""
        config_schema_path = ROOT / "data" / "config.schema.json"
        trace_schema_path = ROOT / "data" / "trace.schema.json"
        
        self.assertTrue(config_schema_path.exists(), "config.schema.json missing")
        self.assertTrue(trace_schema_path.exists(), "trace.schema.json missing")
        
        with config_schema_path.open() as f:
            config_schema = json.load(f)
            self.assertIn("properties", config_schema)
            self.assertIn("disruptions", config_schema["properties"])
            
        with trace_schema_path.open() as f:
            trace_schema = json.load(f)
            self.assertIn("properties", trace_schema)
            self.assertIn("disruption", trace_schema["properties"])
            self.assertIn("replannedSchedule", trace_schema["properties"])

    def _validate_config_structure(self, config_data: dict, allow_specialists: bool = False):
        required_keys = ["heuristics", "resources", "staff", "patients", "demands"]
        for key in required_keys:
            self.assertIn(key, config_data, f"Missing key {key} in config")
            
        self.assertIsInstance(config_data["resources"], list)
        self.assertIsInstance(config_data["staff"], list)
        self.assertIsInstance(config_data["demands"], list)
        
        if allow_specialists:
            # Check specialist fields in staff and demands
            for s in config_data["staff"]:
                self.assertIn("specialty", s, f"Staff {s.get('id')} missing specialty")
                self.assertIn("skills", s)
                
            for d in config_data["demands"]:
                self.assertTrue("requiredTeam" in d or "requiredRoles" in d,
                                f"Demand {d.get('id')} must have requiredTeam or requiredRoles")
                
            if "disruptions" in config_data:
                for dis in config_data["disruptions"]:
                    self.assertIn("id", dis)
                    self.assertIn("type", dis)
                    self.assertIn("staffId", dis)

    def test_data_config_conforms_to_contract(self):
        config_path = ROOT / "data" / "config.json"
        self.assertTrue(config_path.exists())
        with config_path.open() as f:
            data = json.load(f)
        self._validate_config_structure(data, allow_specialists=False)

    def test_mock_config_specialists_fixture(self):
        fixture_path = ROOT / "fixtures" / "mock_config_specialists.json"
        self.assertTrue(fixture_path.exists())
        with fixture_path.open() as f:
            data = json.load(f)
        self._validate_config_structure(data, allow_specialists=True)
        self.assertIn("disruptions", data)
        self.assertGreater(len(data["disruptions"]), 0)
        self.assertEqual(data["disruptions"][0]["type"], "UNPLANNED_SICK_LEAVE")

    def _validate_trace_entry(self, entry: dict):
        required_keys = ["step", "metrics", "schedules", "code"]
        for key in required_keys:
            self.assertIn(key, entry, f"Missing key {key} in trace entry")
        self.assertIsInstance(entry["step"], int)
        self.assertIsInstance(entry["metrics"], dict)
        self.assertIsInstance(entry["schedules"], list)
        
        if "disruption" in entry:
            self.assertIn("type", entry["disruption"])
        if "replannedSchedule" in entry:
            self.assertIsInstance(entry["replannedSchedule"], list)

    def test_mock_trace_replan_fixture(self):
        fixture_path = ROOT / "fixtures" / "mock_trace_replan.jsonl"
        self.assertTrue(fixture_path.exists())
        entries = []
        with fixture_path.open() as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
        self.assertGreaterEqual(len(entries), 2)
        for entry in entries:
            self._validate_trace_entry(entry)
        # Find replan entry with disruption and replannedSchedule
        replan_entry = next((e for e in entries if "disruption" in e), entries[1])
        self.assertIn("disruption", replan_entry)
        self.assertIn("replannedSchedule", replan_entry)
        self.assertEqual(replan_entry["disruption"]["type"], "UNPLANNED_SICK_LEAVE")

    def test_existing_traces_conform(self):
        trace_path = ROOT / "data" / "traces_low.jsonl"
        if not trace_path.exists():
            self.skipTest("traces_low.jsonl not generated")
        with trace_path.open() as f:
            for i, line in enumerate(f):
                if line.strip():
                    entry = json.loads(line.strip())
                    self._validate_trace_entry(entry)
                    if i >= 5:  # Test first few entries for speed
                        break

if __name__ == "__main__":
    unittest.main()
