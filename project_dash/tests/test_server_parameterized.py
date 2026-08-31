"""Parameterized server endpoint tests across projects (sample, monaro, f-dse)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

import server
from tests.conftest import DummyHandler


def test_get_project_dir_helper():
    """Verify get_project_dir correctly resolves project folders with fallback."""
    sample_dir = server.get_project_dir("sample")
    assert Path(sample_dir).exists()
    assert sample_dir.endswith(str(Path("data") / "sample"))

    monaro_dir = server.get_project_dir("monaro")
    assert Path(monaro_dir).exists()
    assert monaro_dir.endswith(str(Path("data") / "monaro")) or monaro_dir.endswith(str(Path("data") / "f-dse"))

    fdse_dir = server.get_project_dir("f-dse")
    assert Path(fdse_dir).exists()
    assert fdse_dir.endswith(str(Path("data") / "monaro")) or fdse_dir.endswith(str(Path("data") / "f-dse"))

    # Default fallback
    default_dir = server.get_project_dir("")
    assert Path(default_dir).exists()


@pytest.mark.parametrize("project_query, min_risks", [
    ("project=sample", 20),
    ("project=monaro", 100),
    ("project=f-dse", 100),
])
def test_sync_sheet_parameterized(dummy_handler: DummyHandler, project_query: str, min_risks: int):
    """Verify handle_sync_sheet returns correct risks and snapshots across projects and aliases."""
    server.DashboardHandler.handle_sync_sheet(dummy_handler, query_str=project_query)
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert "risks" in dummy_handler.sent_data
    assert "issues" in dummy_handler.sent_data
    assert "snapshots" in dummy_handler.sent_data
    assert len(dummy_handler.sent_data["risks"]) >= min_risks


def test_check_drive_sync_parameterized(dummy_handler: DummyHandler):
    """Verify check_drive_sync returns correct snapshot count per project."""
    server.DashboardHandler.handle_check_drive_sync(dummy_handler, query_str="project=sample")
    assert dummy_handler.sent_code == 200
    assert "snapshots" in dummy_handler.sent_data
    assert "w27" in dummy_handler.sent_data["snapshots"]


def test_handle_ingest_data_endpoint(dummy_handler: DummyHandler):
    """Verify POST /api/ingest-data triggers ingestion orchestrator."""
    server.DashboardHandler.handle_ingest_data(dummy_handler, params={"project": "sample"})
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data.get("status") == "ok"
    assert dummy_handler.sent_data.get("project") == "sample"
    assert "message" in dummy_handler.sent_data


def test_handle_sync_all_endpoint(dummy_handler: DummyHandler):
    """Verify /api/sync-all runs full multi-source sync and returns summary counts."""
    server.DashboardHandler.handle_sync_all(dummy_handler, query_or_params={"project": "sample"})
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data.get("status") == "ok"
    assert dummy_handler.sent_data.get("project") == "sample"
    assert "summary" in dummy_handler.sent_data
    assert "snapshots" in dummy_handler.sent_data["summary"]


def test_handle_regenerate_briefing_endpoint(dummy_handler: DummyHandler):
    """Verify POST /api/regenerate-briefing regenerates briefing synthesis."""
    server.DashboardHandler.handle_regenerate_briefing(dummy_handler, params={"project": "sample", "week": "Week 27", "fallback": True})
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data.get("status") == "ok"


def test_check_drive_sync_reconciles_nested_drive_file_and_week_labels(dummy_handler: DummyHandler):
    """Verify Bug #83: handle_check_drive_sync recognizes snapshots with nested driveFile dicts and week labels."""
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

        server.DashboardHandler.handle_check_drive_sync(dummy_handler, query_str="project=monaro")
        assert dummy_handler.sent_code == 200
        assert dummy_handler.sent_data.get("uningestedCount") == 0
        assert len(dummy_handler.sent_data.get("uningestedReports")) == 0
        w28_rep = next((r for r in dummy_handler.sent_data.get("allReports", []) if r.get("week") == "Week 28"), None)
        assert w28_rep is not None
        assert w28_rep["isIngested"] is True


def test_check_drive_sync_queries_live_folder_on_demand_and_merges_real_urls(dummy_handler: DummyHandler):
    """Verify Bug #84 & #85: handle_check_drive_sync queries live Drive folder on demand and uses real Drive URLs."""
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

        server.DashboardHandler.handle_check_drive_sync(dummy_handler, query_str="project=monaro")
        assert dummy_handler.sent_code == 200
        # Verify query_live_drive_folder was called with Monaro's configured folderId
        mock_live_query.assert_called_once_with("1JIsbi35mXn4W-NxjbLTWo22FQMv_zv-C")

        all_reps = dummy_handler.sent_data.get("allReports", [])
        w29_rep = next((r for r in all_reps if r.get("week") == "Week 29"), None)
        assert w29_rep is not None
        assert w29_rep["id"] == "real_gdrive_w29_id_xyz"
        assert w29_rep["url"] == "https://drive.google.com/file/d/real_gdrive_w29_id_xyz/view"
        # Week 29 is uningested so uningestedReports includes it
        uningested = dummy_handler.sent_data.get("uningestedReports", [])
        assert any(r.get("week") == "Week 29" for r in uningested)
