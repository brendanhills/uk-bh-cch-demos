#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase2Bugs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(cls.index_path, "r", encoding="utf-8") as f:
            cls.html = f.read()

    def test_bug_28_and_35_workspace_sync_modal_4_streams(self):
        """Bugs #28 & #35: Workspace Live Sync modal must include Team Google and NotebookLM streams."""
        self.assertIn('id="sheetsModal"', self.html, "sheetsModal must exist")
        idx = self.html.find('id="sheetsModal"')
        idx_end = self.html.find('<!-- SCRIPT CONTROLLERS -->')
        modal_html = self.html[idx:idx_end]

        # Must include Team Google Sheet link
        self.assertIn("1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA", modal_html, "sheetsModal must link to Team Google Sheet")
        # Must include NotebookLM link
        self.assertIn("acdbb29b-8632-4fc7-9ba8-2357beeff141", modal_html, "sheetsModal must link to NotebookLM")
        # Must include Notebook sync trigger
        self.assertTrue(
            "triggerNotebookSync" in modal_html or "syncAllWorkspaceSources" in modal_html,
            "sheetsModal must provide a trigger to sync NotebookLM and all sources"
        )

    def test_bug_27_exec_briefing_synthesizes_team_google_and_blueprints(self):
        """Bug #27: Executive briefing must synthesize Team Google and Blueprint datasets."""
        self.assertIn("function renderExecBriefing", self.html, "renderExecBriefing must be defined")
        idx = self.html.find("function renderExecBriefing")
        exec_body = self.html[idx:idx+4000]
        
        # Must reference LIVE_TEAM_GOOGLE_RISKS in synthesis or KPIs
        self.assertTrue(
            "LIVE_TEAM_GOOGLE_RISKS" in exec_body or "teamGoogle" in exec_body or "Team Google" in exec_body,
            "renderExecBriefing must include Team Google risks in synthesis"
        )
        # Must reference Notebook or Blueprint mappings
        self.assertTrue(
            "NOTEBOOK_CATALOG" in exec_body or "BUNDLE_ANNEX_MAPPING" in exec_body or "Blueprint" in exec_body or "NotebookLM" in exec_body,
            "renderExecBriefing must link or reference contract blueprint intelligence"
        )

if __name__ == "__main__":
    unittest.main()
