#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase1Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = "/usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash/index.html"
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_bug_30_matrix_cell_click_clears_stale_search(self):
        """Bug #30: Clicking a 5x5 heatmap cell must clear conflicting search text."""
        self.assertIn("function highlightHeatmapCell", self.html, "highlightHeatmapCell must be defined")
        idx = self.html.find("function highlightHeatmapCell")
        idx_end = self.html.find("function initApp", idx)
        body = self.html[idx:idx_end] if idx_end != -1 else self.html[idx:idx+2500]
        self.assertTrue(
            "explorerSearchInput" in body and ("value = ''" in body or "value=''" in body),
            "highlightHeatmapCell must reset explorerSearchInput so stale text does not filter out cell risks"
        )

    def test_bug_33_blueprint_bundle_filter_matches_mapped_risks(self):
        """Bug #33: Blueprint bundle filter must filter risks using BUNDLE_ANNEX_MAPPING."""
        self.assertIn("function filterRiskExplorerByBundle", self.html, "filterRiskExplorerByBundle must be defined")
        idx = self.html.find("function renderRiskExplorer")
        idx_end = self.html.find("function renderMatrix", idx)
        render_body = self.html[idx:idx_end] if idx_end != -1 else self.html[idx:idx+4000]
        self.assertTrue(
            "BUNDLE_ANNEX_MAPPING" in render_body and ("jointRisks" in render_body or "activeJointRiskCount" in render_body),
            "renderRiskExplorer must evaluate bundle membership via BUNDLE_ANNEX_MAPPING or bundle tags"
        )

    def test_bug_34_team_google_cards_have_click_drilldown(self):
        """Bug #34: Team Google Risk Explorer cards must support click-to-drill-down / modal inspection."""
        self.assertIn("renderTeamGoogleRiskExplorer", self.html, "renderTeamGoogleRiskExplorer must be defined")
        idx = self.html.find("function renderTeamGoogleRiskExplorer")
        idx_end = self.html.find("function initApp", idx)
        tg_body = self.html[idx:idx_end] if idx_end != -1 else self.html[idx:idx+5000]
        self.assertIn(
            "openItemDetailModal",
            tg_body,
            "Team Google risk cards in renderTeamGoogleRiskExplorer must have openItemDetailModal click handler"
        )

    def test_bug_31_team_google_matrix_standardized_layout(self):
        """Bug #31: Team Google 5x5 heatmap must follow the standardized 5x5 matrix layout."""
        self.assertIn("renderTeamGoogleHeatmap", self.html, "renderTeamGoogleHeatmap must be defined")
        idx = self.html.find("function renderTeamGoogleHeatmap")
        idx_end = self.html.find("function initApp", idx)
        tg_body = self.html[idx:idx_end] if idx_end != -1 else self.html[idx:idx+5000]
        self.assertTrue(
            "filterTeamGoogleMatrixCell" in tg_body or "teamGoogleActiveMatrixCellFilter" in tg_body,
            "Team Google heatmap cells must have interactive cell click filtering"
        )

if __name__ == "__main__":
    unittest.main()
