import unittest
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhase1Stability(unittest.TestCase):
    def setUp(self):
        self.fdse_dir = os.path.join(BASE_DIR, 'data', 'f-dse')
        with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
            self.html = f.read()

    def test_fdse_data_files_exist_and_valid(self):
        """Verify all F-DSE project raw data files exist and parse as valid JSON."""
        required_files = [
            'config.json', 'risks.json', 'issues.json', 'snapshots.json',
            'driver_tree.json', 'knowledge.json'
        ]
        for filename in required_files:
            file_path = os.path.join(self.fdse_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Missing data file: {filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.assertIsNotNone(data)

    def test_fdse_knowledge_sources_has_annexes(self):
        """Verify F-DSE knowledge.json contains solution blueprint annexes."""
        k_file = os.path.join(self.fdse_dir, 'knowledge.json')
        with open(k_file, 'r', encoding='utf-8') as f:
            k = json.load(f)

        sources = k.get('sources', [])
        blueprints = [s for s in sources if s.get('bundle')]
        self.assertGreaterEqual(len(blueprints), 10, "Expected at least 10 blueprint bundle sources in F-DSE knowledge")

    def test_driver_tree_normalization_in_html(self):
        """Verify index.html normalizes description, completeBy, and progress."""
        self.assertIn("description: g.description || g.name || g.title", self.html)
        self.assertIn("completeBy: g.completeBy || g.dueDate || g.targetDate", self.html)
        self.assertIn("progress: g.progress !== undefined ? g.progress", self.html)

    def test_dynamic_timeline_metrics_in_html(self):
        """Verify computeTimelineMetrics computes dynamically across snapshots."""
        self.assertIn("function computeTimelineMetrics(granularity)", self.html)
        self.assertNotIn("PRECOMPUTED_ANALYTICS", self.html)

    def test_top5_resilience_in_html(self):
        """Verify renderTop5Risks and renderTop5Issues have name fallbacks and empty states."""
        self.assertIn("r.riskName || r.riskTitle || r.riskDescription || r.title", self.html)
        self.assertIn("i.issueName || i.issueTitle || i.issueDescription", self.html)
        self.assertIn("No active risks recorded", self.html)
        self.assertIn("No active escalated issues recorded", self.html)

    def test_team_google_status_filter_clears_matrix_cell(self):
        """Verify setTeamGoogleStatusFilter resets active matrix cell filter."""
        self.assertIn("teamGoogleActiveMatrixCellFilter = null;", self.html)

    def test_header_controls_flex_nowrap_and_no_dropdown(self):
        """Verify header action bar has flex-nowrap and dropdown is removed."""
        self.assertIn("flex items-center gap-2 flex-nowrap shrink-0", self.html)
        self.assertNotIn("id=\"projectDropdownMenu\"", self.html)
        self.assertIn("data:image/svg+xml,", self.html)

    def test_podcast_script_resolution_and_speech_synthesis(self):
        """Verify getPodcastScriptForWeek is called for rendering, copying, and speaking podcast."""
        self.assertIn("const script = getPodcastScriptForWeek(activeTimeMachineWeek);", self.html)
        self.assertIn("window.speechSynthesis.speak(utterance);", self.html)
        self.assertIn("function toggleTranscriptModal()", self.html)
        
    def test_fdse_driver_tree_has_24_gates_and_levels(self):
        """Verify F-DSE driver_tree.json contains all 24 gates and both L2/L3 levels (Bug #70)."""
        dt_file = os.path.join(self.fdse_dir, 'driver_tree.json')
        with open(dt_file, 'r', encoding='utf-8') as f:
            dt = json.load(f)
        
        all_gates = []
        for cd in dt.get('capabilityDrops', []):
            all_gates.extend(cd.get('gates', []))
        
        self.assertEqual(len(all_gates), 24, "Expected exactly 24 contractual capability drop gates")
        l2_gates = [g for g in all_gates if g.get('level') == 2]
        l3_gates = [g for g in all_gates if g.get('level') == 3]
        self.assertGreaterEqual(len(l2_gates), 10, "Expected at least 10 Level 2 Primary Gates")
        self.assertGreaterEqual(len(l3_gates), 10, "Expected at least 10 Level 3 Work Packages")

    def test_header_dual_sheet_dropdown(self):
        """Verify header action bar has dual Google Sheets dropdown (Bug #56)."""
        self.assertIn("id=\"sheetDropdownWrapper\"", self.html)
        self.assertIn("id=\"headerJointSheetLink\"", self.html)
        self.assertIn("id=\"headerTeamGoogleSheetLink\"", self.html)
        self.assertIn("function toggleSheetDropdown", self.html)

    def test_sleeper_outlier_conditional_hide(self):
        """Verify sleeper outlier hides container when empty and normalizes properties (Bug #71)."""
        self.assertIn("slContainer.classList.add('hidden');", self.html)
        self.assertIn("sl.risk || sl.description || sl.title", self.html)
        self.assertIn("sl.trigger || sl.triggerCondition || sl.action", self.html)

    def test_gap_close_plan_id_and_jump(self):
        """Verify gap close plan cards have unique IDs and jumpToGapClose handles direct lookup (Bug #53)."""
        self.assertIn("id=\"gapPlan_${g.num}\"", self.html)
        self.assertIn("document.getElementById(`gapPlan_${cleanNum}`)", self.html)
        self.assertIn("↑ Briefing", self.html)
        self.assertIn("jumpToGapClose('${gapNum}')", self.html)

    def test_podcast_studio_audio_asset_and_priority(self):
        """Verify authentic natural audio files exist and audio element is prioritized (Bug #72)."""
        w27_mp3 = os.path.join(BASE_DIR, 'assets', 'podcast_w27.mp3')
        self.assertTrue(os.path.exists(w27_mp3), "Missing assets/podcast_w27.mp3")
        self.assertGreater(os.path.getsize(w27_mp3), 100000, "podcast_w27.mp3 must be a real audio file >100KB")
        self.assertIn("const audioEl = document.getElementById('nativePodcastAudio');", self.html)
        self.assertIn("audioEl.play()", self.html)

if __name__ == '__main__':
    unittest.main()
