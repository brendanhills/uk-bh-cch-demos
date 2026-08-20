import unittest
import json
import os
import io
import urllib.parse
from unittest.mock import patch, MagicMock
import server

class TestServerParameterized(unittest.TestCase):
    def setUp(self):
        self.directory = server.DIRECTORY

    def test_get_project_dir_helper(self):
        """Verify get_project_dir correctly resolves project folders with fallback."""
        sample_dir = server.get_project_dir("sample")
        self.assertTrue(os.path.exists(sample_dir))
        self.assertTrue(sample_dir.endswith(os.path.join("data", "sample")))

        fdse_dir = server.get_project_dir("f-dse")
        self.assertTrue(os.path.exists(fdse_dir))
        self.assertTrue(fdse_dir.endswith(os.path.join("data", "f-dse")))

        # Default fallback
        default_dir = server.get_project_dir("")
        self.assertTrue(os.path.exists(default_dir))

    def test_sync_sheet_sample_project(self):
        """Verify handle_sync_sheet returns sample risks and issues when project=sample."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(dummy, query_str="project=sample")
        self.assertEqual(dummy.sent_code, 200)
        self.assertIsNotNone(dummy.sent_data)
        self.assertIn("risks", dummy.sent_data)
        self.assertIn("issues", dummy.sent_data)
        self.assertIn("snapshots", dummy.sent_data)
        # Sample dataset has 28 risks
        self.assertGreaterEqual(len(dummy.sent_data["risks"]), 20)

    def test_sync_sheet_fdse_project(self):
        """Verify handle_sync_sheet returns F-DSE risks when project=f-dse."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(dummy, query_str="project=f-dse")
        self.assertEqual(dummy.sent_code, 200)
        self.assertIsNotNone(dummy.sent_data)
        # F-DSE dataset has 100+ risks
        self.assertGreaterEqual(len(dummy.sent_data["risks"]), 100)

    def test_check_drive_sync_parameterized(self):
        """Verify check_drive_sync returns correct snapshot count per project."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_check_drive_sync(dummy, query_str="project=sample")
        self.assertEqual(dummy.sent_code, 200)
        self.assertIn("snapshots", dummy.sent_data)
        self.assertIn("w27", dummy.sent_data["snapshots"])

    def test_handle_ingest_data_endpoint(self):
        """Verify POST /api/ingest-data triggers ingestion orchestrator."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_ingest_data(dummy, params={"project": "sample"})
        self.assertEqual(dummy.sent_code, 200)
        self.assertEqual(dummy.sent_data.get("status"), "ok")
        self.assertEqual(dummy.sent_data.get("project"), "sample")
        self.assertIn("message", dummy.sent_data)

    def test_handle_sync_all_endpoint(self):
        """Verify /api/sync-all runs full multi-source sync and returns summary counts."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_all(dummy, query_or_params={"project": "sample"})
        self.assertEqual(dummy.sent_code, 200)
        self.assertEqual(dummy.sent_data.get("status"), "ok")
        self.assertEqual(dummy.sent_data.get("project"), "sample")
        self.assertIn("summary", dummy.sent_data)
        self.assertIn("snapshots", dummy.sent_data["summary"])

    def test_handle_regenerate_briefing_endpoint(self):
        """Verify POST /api/regenerate-briefing regenerates briefing synthesis."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_regenerate_briefing(dummy, params={"project": "sample", "week": "w27"})
        self.assertEqual(dummy.sent_code, 200)
        self.assertEqual(dummy.sent_data.get("status"), "ok")
        self.assertIn("synthesis", dummy.sent_data)

if __name__ == "__main__":
    unittest.main()
