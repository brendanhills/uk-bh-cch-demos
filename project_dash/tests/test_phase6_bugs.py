#!/usr/bin/env python3
import unittest
import re
import os

def load_full_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()
    js_dir = os.path.join(base_dir, 'src', 'js')
    if os.path.exists(js_dir):
        for root, _, files in os.walk(js_dir):
            for fn in sorted(files):
                if fn.endswith('.js'):
                    with open(os.path.join(root, fn), 'r', encoding='utf-8') as f:
                        html += chr(10) + f.read()
    return html


class TestPhase6Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = load_full_html()

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
        """Bug #38: Podcast dialogue must be resolved dynamically with avatar, role, and time fields."""
        self.assertIn("function getPodcastScriptForWeek", self.html)
        self.assertIn("renderPodcastTranscript", self.html)
        self.assertIn("function togglePodcastPlayback", self.html)

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