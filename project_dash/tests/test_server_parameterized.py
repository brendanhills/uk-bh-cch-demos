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

        monaro_dir = server.get_project_dir("monaro")
        self.assertTrue(os.path.exists(monaro_dir))
        self.assertTrue(monaro_dir.endswith(os.path.join("data", "monaro")) or monaro_dir.endswith(os.path.join("data", "f-dse")))

        fdse_dir = server.get_project_dir("f-dse")
        self.assertTrue(os.path.exists(fdse_dir))
        self.assertTrue(fdse_dir.endswith(os.path.join("data", "monaro")) or fdse_dir.endswith(os.path.join("data", "f-dse")))

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

    def test_sync_sheet_monaro_project(self):
        """Verify handle_sync_sheet returns Monaro risks when project=monaro."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(dummy, query_str="project=monaro")
        self.assertEqual(dummy.sent_code, 200)
        self.assertIsNotNone(dummy.sent_data)
        self.assertGreaterEqual(len(dummy.sent_data["risks"]), 100)

    def test_sync_sheet_fdse_project(self):
        """Verify handle_sync_sheet returns Monaro risks when project=f-dse via backward-compatibility alias."""
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
        # Monaro/F-DSE dataset has 100+ risks
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

    def test_check_drive_sync_reconciles_nested_drive_file_and_week_labels(self):
        """Verify Bug #83: handle_check_drive_sync recognizes snapshots with nested driveFile dicts and week labels."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        mock_snapshots = {
            "snapshots": {
                "w27": {
                    "weekNumber": 27,
                    "weekLabel": "Week 27",
                    "date": "07 Aug 2026",
                    "driveFileId": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu",
                    "driveFileName": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf"
                },
                "Week 28": {
                    "week": "Week 28",
                    "date": "14 Aug 2026",
                    "driveFile": {
                        "name": "Weekly Reporting - Week 28 - 14 Aug 2026.pdf",
                        "id": "mock-drive-id-28"
                    }
                }
            }
        }

        with patch("server.load_json_file") as mock_load:
            def side_effect(path, default=None):
                if "snapshots.json" in path:
                    return mock_snapshots
                if "config.json" in path:
                    return {
                        "sources": {
                            "googleDrive": {
                                "knownReports": [
                                    {"id": "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "week": "Week 27", "name": "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu/view"},
                                    {"id": "1_monaro_drive_w28", "week": "Week 28", "name": "Weekly Reporting - Week 28 - 14 Aug 2026.pdf", "url": "https://drive.google.com/file/d/1_monaro_drive_w28/view"}
                                ]
                            }
                        }
                    }
                return default or {}
            mock_load.side_effect = side_effect

            dummy = DummyHandler()
            server.DashboardHandler.handle_check_drive_sync(dummy, query_str="project=monaro")
            self.assertEqual(dummy.sent_code, 200)
            self.assertEqual(dummy.sent_data.get("uningestedCount"), 0)
            self.assertEqual(len(dummy.sent_data.get("uningestedReports")), 0)
            w28_rep = next((r for r in dummy.sent_data.get("allReports", []) if r.get("week") == "Week 28"), None)
            self.assertIsNotNone(w28_rep)
            self.assertTrue(w28_rep["isIngested"])

    def test_check_drive_sync_queries_live_folder_on_demand_and_merges_real_urls(self):
        """Verify Bug #84 & #85: handle_check_drive_sync queries live Drive folder on demand and uses real Drive URLs."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        mock_live_reports = [
            {
                "id": "real_gdrive_w29_id_xyz",
                "name": "Weekly Reporting - Week 29 - 21 Aug 2026.pdf",
                "week": "Week 29",
                "date": "21 Aug 2026",
                "url": "https://drive.google.com/file/d/real_gdrive_w29_id_xyz/view"
            },
            {
                "id": "real_gdrive_w28_id_abc",
                "name": "Weekly Reporting - Week 28 - 14 Aug 2026.pdf",
                "week": "Week 28",
                "date": "14 Aug 2026",
                "url": "https://drive.google.com/file/d/real_gdrive_w28_id_abc/view"
            }
        ]

        with patch("server.query_live_drive_folder") as mock_live_query:
            mock_live_query.return_value = mock_live_reports

            dummy = DummyHandler()
            server.DashboardHandler.handle_check_drive_sync(dummy, query_str="project=monaro")
            self.assertEqual(dummy.sent_code, 200)
            # Verify query_live_drive_folder was called with Monaro's configured folderId
            mock_live_query.assert_called_once_with("1JIsbi35mXn4W-NxjbLTWo22FQMv_zv-C")

            all_reps = dummy.sent_data.get("allReports", [])
            w29_rep = next((r for r in all_reps if r.get("week") == "Week 29"), None)
            self.assertIsNotNone(w29_rep)
            self.assertEqual(w29_rep["id"], "real_gdrive_w29_id_xyz")
            self.assertEqual(w29_rep["url"], "https://drive.google.com/file/d/real_gdrive_w29_id_xyz/view")
            # Week 29 is uningested so uningestedReports includes it
            uningested = dummy.sent_data.get("uningestedReports", [])
            self.assertTrue(any(r.get("week") == "Week 29" for r in uningested))

if __name__ == "__main__":
    unittest.main()
