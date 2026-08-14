import unittest
import server

class TestServerStartup(unittest.TestCase):
    def test_get_startup_urls(self):
        """Verify server provides clickable URLs on startup."""
        self.assertTrue(hasattr(server, 'get_startup_urls'), "server.py should have get_startup_urls function")
        urls = server.get_startup_urls(9000)
        self.assertIn("http://localhost:9000", urls)
        self.assertIn("http://127.0.0.1:9000", urls)

    def test_startup_banner_output(self):
        """Verify startup banner contains clickable URL."""
        self.assertTrue(hasattr(server, 'get_startup_banner'), "server.py should have get_startup_banner function")
        banner = server.get_startup_banner(9000)
        self.assertIn("http://localhost:9000", banner)
        self.assertIn("http://127.0.0.1:9000", banner)

class TestDriveSync(unittest.TestCase):
    def test_week27_in_known_drive_reports(self):
        """Verify Week 27 pack is present in KNOWN_DRIVE_REPORTS."""
        self.assertTrue(hasattr(server, 'KNOWN_DRIVE_REPORTS'))
        week27_reports = [r for r in server.KNOWN_DRIVE_REPORTS if r.get('week') == 'Week 27' or 'Week 27' in r.get('name', '')]
        self.assertGreaterEqual(len(week27_reports), 1, "Week 27 must be present in KNOWN_DRIVE_REPORTS")
        self.assertEqual(week27_reports[0]['id'], "1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu")

    def test_week27_ingestion_pipeline(self):
        """Verify Week 27 ingest script parses and returns valid snapshot."""
        from scripts.ingest_weekly_report import ingest_file
        snapshot = ingest_file("1HBfI9itx3BER4IRnH9eavBgAsrDGHnmu", "Weekly Reporting - Week 27 - 07 Aug 2026.pdf", 27, "07 Aug 2026")
        self.assertEqual(snapshot['weekNumber'], 27)
        self.assertEqual(snapshot['weekLabel'], "Week 27")
        self.assertTrue(snapshot['isLatest'])
        self.assertEqual(len(snapshot['plans']), 5)

    def test_snapshots_data_integrity(self):
        """Verify weekly_snapshots.json contains Week 27 marked as current/latest."""
        import json, os
        snapshots_path = os.path.join(server.DIRECTORY, "src", "data", "weekly_snapshots.json")
        self.assertTrue(os.path.exists(snapshots_path), "weekly_snapshots.json must exist")
        with open(snapshots_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        snapshots = data.get("snapshots", {})
        self.assertIn("w27", snapshots, "Week 27 snapshot must be present in snapshots")
        self.assertTrue(snapshots["w27"].get("isCurrent") or snapshots["w27"].get("isLatest"), "Week 27 must be current/latest")
        self.assertEqual(snapshots["w27"]["week"], "Week 27")

    def test_sync_sheet_handler_includes_snapshots(self):
        """Verify DashboardHandler handle_sync_sheet payload includes snapshots."""
        import json, io
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code
        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(dummy)
        self.assertEqual(dummy.sent_code, 200)
        self.assertIsNotNone(dummy.sent_data)
        self.assertIn('snapshots', dummy.sent_data)
        self.assertIn('w27', dummy.sent_data['snapshots'])

    def test_check_drive_sync_handler_includes_week27(self):
        """Verify DashboardHandler handle_check_drive_sync recognizes Week 27."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code
        dummy = DummyHandler()
        server.DashboardHandler.handle_check_drive_sync(dummy)
        self.assertEqual(dummy.sent_code, 200)
        self.assertIsNotNone(dummy.sent_data)
        self.assertIn('allReports', dummy.sent_data)
        w27_reports = [r for r in dummy.sent_data['allReports'] if r.get('week') == 'Week 27']
        self.assertGreaterEqual(len(w27_reports), 1)
        self.assertTrue(w27_reports[0]['isIngested'])

class TestAllDashboardsDynamicSync(unittest.TestCase):
    """Verify all dashboard views in index.html are dynamically bound to live sync and active week."""
    @classmethod
    def setUpClass(cls):
        import os
        index_path = os.path.join(server.DIRECTORY, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            cls.html_content = f.read()

    def test_view_containers_exist(self):
        """Verify all 6 tab view containers exist."""
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
            self.assertIn(v, self.html_content, f"View container {v} must exist in index.html")

    def test_sync_updates_all_views(self):
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
            self.assertIn(call, self.html_content, f"syncGoogleSheet must invoke {call}")

    def test_driver_tree_deck_link_and_badge_dynamic(self):
        """Verify Driver Tree header has dynamic deck link and reference badge elements."""
        self.assertIn('id="driverTreeRefBadge"', self.html_content)
        self.assertIn('id="driverTreeDeckLink"', self.html_content)

    def test_time_machine_modal_dynamic_container(self):
        """Verify Time Machine modal uses dynamic container."""
        self.assertIn('id="timeMachineSnapshotsList"', self.html_content)
        self.assertIn('renderTimeMachineModalList', self.html_content)

    def test_trends_badge_dynamic(self):
        """Verify trends period badge is dynamic."""
        self.assertIn('id="trendsTodayBadge"', self.html_content)

    def test_heatmap_status_counts_dynamic(self):
        """Verify heatmap status count buttons exist and are referenced."""
        for btn_id in ['rBtnOpen', 'rBtnActive', 'rBtnEventuated', 'rBtnClosed', 'rBtnAll']:
            self.assertIn(f'id="{btn_id}"', self.html_content)

    def test_snapshots_week_properties_defined(self):
        """Verify all snapshots in weekly_snapshots.json have valid week and weekLabel properties (no undefined)."""
        import json, os
        snapshots_path = os.path.join(server.DIRECTORY, "src", "data", "weekly_snapshots.json")
        with open(snapshots_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        snapshots = data.get("snapshots", {})
        for key, snap in snapshots.items():
            self.assertIn("week", snap, f"Snapshot {key} must have 'week' property")
            self.assertIn("weekLabel", snap, f"Snapshot {key} must have 'weekLabel' property")
            self.assertTrue(str(snap["week"]).startswith("Week "), f"Snapshot {key} week must start with 'Week ', got {snap.get('week')}")

    def test_risk_severity_profile_rendered_in_trends(self):
        """Verify Risk Severity Profile container is populated by renderTrendsCharts."""
        self.assertIn('id="riskSeverityProfileContainer"', self.html_content)
        self.assertIn('renderRiskSeverityProfile()', self.html_content)
        # Check that renderRiskSeverityProfile is called inside renderTrendsCharts
        trends_code = self.html_content.split('function renderTrendsCharts()')[1].split('// --- RISK HEATMAP ---')[0]
        self.assertIn('renderRiskSeverityProfile', trends_code, "renderTrendsCharts must invoke renderRiskSeverityProfile")

    def test_diff_baseline_selector_dynamically_populated(self):
        """Verify baseline diff comparison selector is dynamically rendered from snapshots."""
        self.assertIn('id="diffBaselineSelector"', self.html_content)
        self.assertIn('renderDiffBaselineSelector', self.html_content)

    def test_trends_charts_dynamic_timeline_function(self):
        """Verify dynamic timeline metrics computation function exists."""
        self.assertIn('computeTimelineMetrics', self.html_content)

    def test_drilldown_handlers_exist(self):
        """Verify interactive drill-down helper functions exist and are wired."""
        self.assertIn('drillDownToCategory', self.html_content)
        self.assertIn('drillDownToScoreBand', self.html_content)
        self.assertIn('drillDownToCategory(cat)', self.html_content)
        self.assertIn('drillDownToScoreBand', self.html_content)

    def test_baseline_diffing_dynamic(self):
        """Verify baseline diff comparison dynamically compares active vs baseline snapshot."""
        self.assertIn('setDiffBaseline', self.html_content)
        self.assertIn('selectedDiffBaseline', self.html_content)
        self.assertIn('activeTimeMachineWeek !== selectedDiffBaseline', self.html_content)

    def test_kpi_pill_wrapping_classes(self):
        """Verify Bug #23: ATO-C gate and KPI pills have whitespace-nowrap and shrink-0 to prevent awkward wrapping."""
        self.assertIn('id="cardKpiAto"', self.html_content)
        self.assertIn('whitespace-nowrap shrink-0', self.html_content)
        # Verify updateAtoGateKpi preserves whitespace-nowrap and shrink-0
        ato_func_code = self.html_content.split('function updateAtoGateKpi(')[1].split('function switchTab(')[0]
        self.assertIn('whitespace-nowrap shrink-0', ato_func_code)

    def test_timeline_drilldown_modal_and_interaction(self):
        """Verify Bug #25: Timeline charts configure index interaction mode and open drill-down modal."""
        self.assertIn('id="timelineDrilldownModal"', self.html_content)
        self.assertIn('openTimelineDrilldownModal', self.html_content)
        self.assertIn("mode: 'index'", self.html_content)
        self.assertIn("intersect: false", self.html_content)


    def test_team_google_tab_and_renderers_exist(self):
        """Verify Team Google navigation tab and renderer functions exist in index.html."""
        self.assertIn('id="tab-team-google"', self.html_content)
        self.assertIn('renderTeamGoogleHeatmap', self.html_content)
        self.assertIn('renderTeamGoogleRiskExplorer', self.html_content)
        self.assertIn('id="matrixGridTeamGoogle"', self.html_content)
        self.assertIn('id="teamGoogleRiskListContainer"', self.html_content)

    def test_sync_sheet_includes_multi_registers(self):
        """Verify DashboardHandler handle_sync_sheet payload includes teamGoogleRisks and registers metadata."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code
        dummy = DummyHandler()
        server.DashboardHandler.handle_sync_sheet(dummy)
        self.assertEqual(dummy.sent_code, 200)
        self.assertIn('teamGoogleRisks', dummy.sent_data)
        self.assertIn('registers', dummy.sent_data)
        self.assertIn('joint', dummy.sent_data['registers'])
        self.assertIn('teamGoogle', dummy.sent_data['registers'])


    def test_notebook_sync_endpoints(self):
        """Verify DashboardHandler handle_check_notebook_sync and handle_sync_notebook return 200 and valid catalogs."""
        class DummyHandler:
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code
        
        # Test check sync
        dummy1 = DummyHandler()
        server.DashboardHandler.handle_check_notebook_sync(dummy1)
        self.assertEqual(dummy1.sent_code, 200)
        self.assertIn('sources', dummy1.sent_data)
        self.assertEqual(dummy1.sent_data['totalSources'], 17)
        self.assertIn('bundleMapping', dummy1.sent_data)

        # Test sync trigger
        dummy2 = DummyHandler()
        server.DashboardHandler.handle_sync_notebook(dummy2)
        self.assertEqual(dummy2.sent_code, 200)
        self.assertEqual(dummy2.sent_data['status'], 'ok')

    def test_blueprints_tab_and_renderers_exist(self):
        """Verify Blueprint Knowledge navigation tab and renderer functions exist in index.html."""
        self.assertIn('id="tab-blueprints"', self.html_content)
        self.assertIn('renderBlueprintKnowledge', self.html_content)
        self.assertIn('id="bundleAnnexCardsContainer"', self.html_content)
        self.assertIn('id="researchDocsContainer"', self.html_content)
        self.assertIn('id="notebookSelectorSelect"', self.html_content)
        self.assertIn('switchActiveNotebook', self.html_content)

    def test_multi_notebook_registry_and_endpoints(self):
        """Verify multi-notebook registry file and /api/notebooks endpoint."""
        class DummyHandler(server.DashboardHandler):
            def __init__(self):
                self.sent_data = None
                self.sent_code = None
            def send_json(self, data, status_code=200):
                self.sent_data = data
                self.sent_code = status_code

        dummy = DummyHandler()
        server.DashboardHandler.handle_list_notebooks(dummy)
        self.assertEqual(dummy.sent_code, 200)
        self.assertIn('notebooks', dummy.sent_data)
        self.assertGreaterEqual(len(dummy.sent_data['notebooks']), 1)

if __name__ == "__main__":
    unittest.main()

