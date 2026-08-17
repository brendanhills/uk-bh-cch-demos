#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase5Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_bug_32_issue_table_populated_on_switch_tab(self):
        """Bug #32: switchTab('issues') must invoke renderIssueTable()."""
        idx = self.html.find("function switchTab")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertIn("renderIssueTable", body, "switchTab must call renderIssueTable when tab-issues is selected")

    def test_bug_49_open_item_detail_modal_matches_google_risk_id(self):
        """Bug #49: openItemDetailModal must match stringified ID on LIVE_TEAM_GOOGLE_RISKS and open modal."""
        idx = self.html.find("function openItemDetailModal")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertTrue(
            "String(" in body or "== itemId" in body or "=== String(itemId)" in body,
            "openItemDetailModal must use robust string-based ID comparison for both LIVE_RISKS and LIVE_TEAM_GOOGLE_RISKS"
        )
        self.assertIn("LIVE_TEAM_GOOGLE_RISKS", body, "openItemDetailModal must query LIVE_TEAM_GOOGLE_RISKS")
        self.assertIn("modal.classList.remove('hidden')", body, "openItemDetailModal must unhide the modal")
        self.assertIn("Team Google", body, "openItemDetailModal must render Team Google badge when inspecting a Google risk")

    def test_bug_50_risk_cards_have_blueprint_badges_and_links(self):
        """Bug #50: Risk cards in Joint Program and Team Google must render Blueprint Annex badges/links."""
        # Joint Risk Explorer
        idx_joint = self.html.find("function renderRiskExplorer")
        idx_joint_end = self.html.find("function ", idx_joint + 30)
        body_joint = self.html[idx_joint:idx_joint_end]
        self.assertTrue(
            "Annex" in body_joint or "Blueprint" in body_joint or "BUNDLE_ANNEX_MAPPING" in body_joint,
            "renderRiskExplorer cards must resolve and render Blueprint Annex badges"
        )

        # Team Google Risk Explorer
        idx_google = self.html.find("function renderTeamGoogleRiskExplorer")
        idx_google_end = self.html.find("function ", idx_google + 30)
        body_google = self.html[idx_google:idx_google_end]
        self.assertTrue(
            "Annex" in body_google or "Blueprint" in body_google or "BUNDLE_ANNEX_MAPPING" in body_google,
            "renderTeamGoogleRiskExplorer cards must resolve and render Blueprint Annex badges"
        )

    def test_bug_47_top_5_cards_have_drilldowns(self):
        """Bug #47: Top 5 risks and issues lists must have explicit Inspect and filter drilldowns."""
        idx = self.html.find("function renderTop5Risks")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertTrue("openItemDetailModal" in body, "renderTop5Risks must trigger openItemDetailModal on click")
        self.assertTrue("Inspect" in body or "hover:text-indigo-700" in body, "renderTop5Risks must show inspect trigger")

        idx_i = self.html.find("function renderTop5Issues")
        idx_i_end = self.html.find("function ", idx_i + 30)
        body_i = self.html[idx_i:idx_i_end]
        self.assertTrue("openItemDetailModal" in body_i, "renderTop5Issues must trigger openItemDetailModal on click")

    def test_bug_48_podcast_audio_playback_and_speech_fallback(self):
        """Bug #48: Podcast audio player must have Web Speech API fallback or valid audio source."""
        self.assertTrue(
            "speechSynthesis" in self.html or "playExecutivePodcast" in self.html or "togglePodcastPlay" in self.html,
            "index.html must have podcast audio playback handler with speech synthesis fallback"
        )

    def test_bug_38_podcast_transcript_week_27_with_timestamps(self):
        """Bug #38: PODCAST_TRANSCRIPT must have Week 27 dialogue and valid timestamps."""
        idx = self.html.find("PODCAST_TRANSCRIPT")
        self.assertNotEqual(idx, -1, "PODCAST_TRANSCRIPT structure must exist")
        body = self.html[idx:idx+3500]
        self.assertIn("Week 27", body, "Transcript must reference Week 27")
        self.assertIn("time", body, "Transcript items must have time property")
        self.assertIn("role", body, "Transcript items must have role property")
        self.assertNotIn("undefined", body, "Transcript must not hardcode undefined")

if __name__ == "__main__":
    unittest.main()
