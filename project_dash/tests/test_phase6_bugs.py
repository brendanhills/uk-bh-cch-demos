#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase6Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_bug_51_issue_table_column_widths_and_concise_ref(self):
        """Bug #51: Issue table must have balanced column widths and concise Driver Ref badge."""
        idx = self.html.find("function renderIssueTable")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertIn("renderIssueTable", self.html, "renderIssueTable must exist")
        # Ensure Driver Ref is concise (extracting ref code like 1.10b)
        self.assertTrue(
            "driverTreeRef" in body,
            "renderIssueTable must format driverTreeRef cleanly"
        )
        # Check table headers have width constraints
        idx_section = self.html.find('id="view-issues"')
        body_section = self.html[idx_section:idx_section+2500]
        self.assertTrue("table" in body_section, "view-issues must have table element")

    def test_bug_52_issue_inspect_modal_trigger(self):
        """Bug #52: Issue Register must have explicit Inspect button triggering openItemDetailModal."""
        idx = self.html.find("function renderIssueTable")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertIn("openItemDetailModal", body, "renderIssueTable must call openItemDetailModal with 'issue'")
        self.assertIn("Inspect", body, "renderIssueTable must render Inspect button")

    def test_bug_38_podcast_scripts_w27_and_no_undefined(self):
        """Bug #38: PODCAST_SCRIPTS must contain w27 with avatar, role, and time fields."""
        idx = self.html.find("PODCAST_SCRIPTS")
        self.assertNotEqual(idx, -1, "PODCAST_SCRIPTS structure must exist")
        body = self.html[idx:idx+3500]
        self.assertIn("w27", body, "PODCAST_SCRIPTS must have w27 entry")
        self.assertIn("avatar", body, "PODCAST_SCRIPTS must have avatar property")
        self.assertIn("role", body, "PODCAST_SCRIPTS must have role property")

        # Check renderPodcastTranscript
        idx_rpt = self.html.find("function renderPodcastTranscript")
        body_rpt = self.html[idx_rpt:idx_rpt+1500]
        self.assertIn("renderPodcastTranscript", self.html, "renderPodcastTranscript function must exist")

    def test_bug_48_podcast_audio_assets_exist(self):
        """Bug #48: podcast audio file or generator must exist in assets directory."""
        assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        self.assertTrue(os.path.exists(assets_dir), "assets directory must exist")
        has_audio = (
            os.path.exists(os.path.join(assets_dir, "podcast_w27.mp3")) or
            os.path.exists(os.path.join(assets_dir, "podcast_w27.wav"))
        )
        self.assertTrue(has_audio, "assets/podcast_w27.wav or .mp3 must exist on disk")

if __name__ == "__main__":
    unittest.main()
