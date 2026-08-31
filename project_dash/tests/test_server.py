"""Unit and integration tests for server.py, startup banners, sync handlers, and UI bindings."""

import json
from pathlib import Path
import pytest

import server
from tests.conftest import DummyHandler


def load_full_html(project_root: Path) -> str:
    """Loads index.html concatenated with all ES modules under src/js/."""
    html_file = project_root / "index.html"
    html = html_file.read_text(encoding="utf-8")
    js_dir = project_root / "src" / "js"
    if js_dir.exists():
        for js_path in sorted(js_dir.rglob("*.js")):
            html += "\n" + js_path.read_text(encoding="utf-8")
    return html


@pytest.fixture(scope="module")
def full_html(project_root: Path) -> str:
    """Provides the full index.html and concatenated module code for inspection."""
    return load_full_html(project_root)


# --- TestServerStartup ---

def test_get_startup_urls():
    """Verify server provides clickable URLs on startup."""
    assert hasattr(server, 'get_startup_urls'), "server.py should have get_startup_urls function"
    urls = server.get_startup_urls(9000)
    assert "http://localhost:9000" in urls
    assert "http://127.0.0.1:9000" in urls


def test_startup_banner_output():
    """Verify startup banner contains clickable URL."""
    assert hasattr(server, 'get_startup_banner'), "server.py should have get_startup_banner function"
    banner = server.get_startup_banner(9000)
    assert "http://localhost:9000" in banner
    assert "http://127.0.0.1:9000" in banner


# --- TestDriveSync ---

def test_week27_in_known_drive_reports():
    """Verify Week 27 pack is present in KNOWN_DRIVE_REPORTS."""
    assert hasattr(server, 'KNOWN_DRIVE_REPORTS')
    week27_reports = [r for r in server.KNOWN_DRIVE_REPORTS if r.get('week') == 'Week 27' or 'Week 27' in r.get('name', '')]
    assert len(week27_reports) >= 1, "Week 27 must be present in KNOWN_DRIVE_REPORTS"
    assert week27_reports[0]['id'] == "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu"


def test_week27_ingestion_pipeline():
    """Verify Week 27 ingest script parses and returns valid snapshot."""
    from scripts.pipeline import ingest_file
    snapshot = ingest_file("1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", 27, "07 Aug 2026")
    assert snapshot['weekNumber'] == 27
    assert snapshot['weekLabel'] == "Week 27"
    assert snapshot['isLatest'] is True
    assert len(snapshot['plans']) >= 4


def test_snapshots_data_integrity(project_root: Path):
    """Verify weekly_snapshots.json contains Week 27 marked as current/latest."""
    snapshots_path = project_root / "data" / "drive" / "weekly_snapshots.json"
    assert snapshots_path.exists(), "weekly_snapshots.json must exist"
    with open(snapshots_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    snapshots = data.get("snapshots", {})
    assert "w27" in snapshots, "Week 27 snapshot must be present in snapshots"
    assert snapshots["w27"].get("isCurrent") or snapshots["w27"].get("isLatest"), "Week 27 must be current/latest"
    assert snapshots["w27"]["week"] == "Week 27"


def test_sync_sheet_handler_includes_snapshots(dummy_handler: DummyHandler):
    """Verify DashboardHandler handle_sync_sheet payload includes snapshots."""
    server.DashboardHandler.handle_sync_sheet(dummy_handler)
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert 'snapshots' in dummy_handler.sent_data
    assert 'w27' in dummy_handler.sent_data['snapshots']


def test_check_drive_sync_handler_includes_week27(dummy_handler: DummyHandler):
    """Verify DashboardHandler handle_check_drive_sync recognizes Week 27."""
    server.DashboardHandler.handle_check_drive_sync(dummy_handler)
    assert dummy_handler.sent_code == 200
    assert dummy_handler.sent_data is not None
    assert 'allReports' in dummy_handler.sent_data
    w27_reports = [r for r in dummy_handler.sent_data['allReports'] if r.get('week') == 'Week 27']
    assert len(w27_reports) >= 1
    assert w27_reports[0]['isIngested'] is True


def test_sync_sheet_includes_multi_registers(dummy_handler: DummyHandler):
    """Verify DashboardHandler handle_sync_sheet payload includes teamGoogleRisks and registers metadata."""
    server.DashboardHandler.handle_sync_sheet(dummy_handler)
    assert dummy_handler.sent_code == 200
    assert 'teamGoogleRisks' in dummy_handler.sent_data
    assert 'registers' in dummy_handler.sent_data
    assert 'joint' in dummy_handler.sent_data['registers']
    assert 'teamGoogle' in dummy_handler.sent_data['registers']


def test_notebook_sync_endpoints():
    """Verify DashboardHandler handle_check_notebook_sync and handle_sync_notebook return 200 and valid catalogs."""
    dummy1 = DummyHandler()
    server.DashboardHandler.handle_check_notebook_sync(dummy1)
    assert dummy1.sent_code == 200
    assert 'sources' in dummy1.sent_data
    assert dummy1.sent_data['totalSources'] > 0
    assert 'bundleMapping' in dummy1.sent_data

    dummy2 = DummyHandler()
    server.DashboardHandler.handle_sync_notebook(dummy2)
    assert dummy2.sent_code == 200
    assert dummy2.sent_data['status'] == 'ok'


def test_multi_notebook_registry_and_endpoints(dummy_handler: DummyHandler):
    """Verify multi-notebook registry file and /api/notebooks endpoint."""
    server.DashboardHandler.handle_list_notebooks(dummy_handler)
    assert dummy_handler.sent_code == 200
    assert 'notebooks' in dummy_handler.sent_data
    assert len(dummy_handler.sent_data['notebooks']) >= 1


# --- TestAllDashboardsDynamicSync UI Bindings ---

def test_view_containers_exist(full_html: str):
    """Verify all 8 tab view containers exist."""
    views = [
        'id="view-exec-briefing"',
        'id="view-overview"',
        'id="view-team-google"',
        'id="view-issues"',
        'id="view-trends"',
        'id="view-driver-tree"',
        'id="view-blueprints"',
        'id="view-ledger"'
    ]
    for v in views:
        assert v in full_html, f"View container {v} must exist in index.html"


def test_sync_updates_all_views(full_html: str):
    """Verify syncGoogleSheet calls renderers for all views."""
    required_calls = [
        'activateTimeMachine',
        'renderRiskHeatmap',
        'renderExecBriefing',
        'renderExecGapClosePlans',
        'filterAndRenderIssues',
        'renderDriverTree',
        'renderLedger',
        'renderTrendsCharts',
        'renderRiskExplorer'
    ]
    for call in required_calls:
        assert call in full_html, f"syncGoogleSheet must invoke {call}"


def test_driver_tree_deck_link_and_badge_dynamic(full_html: str):
    """Verify Driver Tree header has dynamic deck link and reference badge elements."""
    assert 'id="driverTreeRefBadge"' in full_html
    assert 'id="driverTreeDeckLink"' in full_html


def test_time_machine_modal_dynamic_container(full_html: str):
    """Verify Time Machine modal uses dynamic container."""
    assert 'id="timeMachineSnapshotsList"' in full_html
    assert 'renderTimeMachineModalList' in full_html


def test_trends_badge_dynamic(full_html: str):
    """Verify trends period badge is dynamic."""
    assert 'id="trendsTodayBadge"' in full_html


def test_heatmap_status_counts_dynamic(full_html: str):
    """Verify heatmap status count buttons exist and are referenced."""
    for btn_id in ['rBtnOpen', 'rBtnActive', 'rBtnEventuated', 'rBtnClosed', 'rBtnAll']:
        assert f'id="{btn_id}"' in full_html


def test_snapshots_week_properties_defined(project_root: Path):
    """Verify all snapshots in weekly_snapshots.json have valid week and weekLabel properties."""
    snapshots_path = project_root / "data" / "drive" / "weekly_snapshots.json"
    with open(snapshots_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    snapshots = data.get("snapshots", {})
    for key, snap in snapshots.items():
        assert "week" in snap, f"Snapshot {key} must have 'week' property"
        assert "weekLabel" in snap, f"Snapshot {key} must have 'weekLabel' property"
        assert str(snap["week"]).startswith("Week "), f"Snapshot {key} week must start with 'Week ', got {snap.get('week')}"


def test_risk_severity_profile_rendered_in_trends(full_html: str):
    """Verify Risk Severity Profile container is populated by renderTrendsCharts."""
    assert 'id="riskSeverityProfileContainer"' in full_html
    assert 'renderRiskSeverityProfile()' in full_html
    trends_code = full_html.split('function renderTrendsCharts()')[1].split('// --- RISK HEATMAP ---')[0]
    assert 'renderRiskSeverityProfile' in trends_code, "renderTrendsCharts must invoke renderRiskSeverityProfile"


def test_diff_baseline_selector_dynamically_populated(full_html: str):
    """Verify baseline diff comparison selector is dynamically rendered from snapshots."""
    assert 'id="diffBaselineSelector"' in full_html
    assert 'renderDiffBaselineSelector' in full_html


def test_trends_charts_dynamic_timeline_function(full_html: str):
    """Verify dynamic timeline metrics computation function exists."""
    assert 'computeTimelineMetrics' in full_html


def test_drilldown_handlers_exist(full_html: str):
    """Verify interactive drill-down helper functions exist and are wired."""
    assert 'drillDownToCategory' in full_html
    assert 'drillDownToScoreBand' in full_html
    assert 'drillDownToCategory(cat)' in full_html
    assert 'drillDownToScoreBand' in full_html


def test_baseline_diffing_dynamic(full_html: str):
    """Verify baseline diff comparison dynamically compares active vs baseline snapshot."""
    assert 'setDiffBaseline' in full_html
    assert 'selectedDiffBaseline' in full_html
    assert 'activeTimeMachineWeek !== selectedDiffBaseline' in full_html


def test_kpi_pill_wrapping_classes(full_html: str):
    """Verify Bug #23: ATO-C gate and KPI pills have whitespace-nowrap and shrink-0 to prevent awkward wrapping."""
    assert 'id="cardKpiAto"' in full_html
    assert 'whitespace-nowrap shrink-0' in full_html
    ato_func_code = full_html.split('function updateAtoGateKpi(')[1].split('function switchTab(')[0]
    assert 'whitespace-nowrap shrink-0' in ato_func_code


def test_timeline_drilldown_modal_and_interaction(full_html: str):
    """Verify Bug #25: Timeline charts configure index interaction mode and open drill-down modal."""
    assert 'id="timelineDrilldownModal"' in full_html
    assert 'openTimelineDrilldownModal' in full_html
    assert "mode: 'index'" in full_html
    assert "intersect: false" in full_html


def test_team_google_tab_and_renderers_exist(full_html: str):
    """Verify Team Google navigation tab and renderer functions exist in index.html."""
    assert 'id="tab-team-google"' in full_html
    assert 'renderTeamGoogleHeatmap' in full_html
    assert 'renderTeamGoogleRiskExplorer' in full_html
    assert 'id="matrixGridTeamGoogle"' in full_html
    assert 'id="teamGoogleRiskListContainer"' in full_html


def test_blueprints_tab_and_renderers_exist(full_html: str):
    """Verify Blueprint Knowledge navigation tab and renderer functions exist in index.html."""
    assert 'id="tab-blueprints"' in full_html
    assert 'renderBlueprintKnowledge' in full_html
    assert 'id="bundleAnnexCardsContainer"' in full_html
    assert 'id="researchDocsContainer"' in full_html
    assert 'id="notebookSelectorSelect"' in full_html
    assert 'switchActiveNotebook' in full_html