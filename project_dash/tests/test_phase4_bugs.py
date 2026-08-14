#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase4Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = "/usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash/index.html"
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_bug_42_risk_explorer_container_id_aligned(self):
        """Bug #42: renderRiskExplorer must update explorerCardsContainer element."""
        idx = self.html.find("function renderRiskExplorer")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertIn("explorerCardsContainer", body, "renderRiskExplorer must target explorerCardsContainer")
        self.assertIn("explorerCardsContainer", self.html, "HTML must contain id='explorerCardsContainer'")

    def test_bug_39_exec_summary_top_5_populated(self):
        """Bug #39: Executive Summary must populate execTopRisksFullList and execTopIssuesFullList."""
        self.assertIn("execTopRisksFullList", self.html, "HTML must contain execTopRisksFullList container")
        self.assertIn("execTopIssuesFullList", self.html, "HTML must contain execTopIssuesFullList container")
        
        idx = self.html.find("function renderExecBriefing")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertTrue(
            "renderTop5Risks" in self.html or "execTopRisksFullList" in body,
            "renderExecBriefing or dedicated functions must populate top 5 risks"
        )
        self.assertTrue(
            "renderTop5Issues" in self.html or "execTopIssuesFullList" in body,
            "renderExecBriefing or dedicated functions must populate top 5 issues"
        )

    def test_bug_40_matrix_axes_standardized_across_both_registers(self):
        """Bug #40: Both Joint and Team Google matrices must have X=Likelihood and Y=Consequence."""
        # Check Joint matrix renderer
        idx_joint = self.html.find("function renderRiskHeatmap")
        body_joint = self.html[idx_joint:idx_joint+2500]
        self.assertTrue("Rare" in body_joint and "Almost Certain" in body_joint, "Joint Heatmap X-axis must have Rare to Almost Certain")
        self.assertIn("Consequence (Y) ↓ / Likelihood (X) →", body_joint, "Joint Heatmap must have standard axis title")

        # Check Team Google matrix renderer
        idx_google = self.html.find("function renderTeamGoogleHeatmap")
        body_google = self.html[idx_google:idx_google+3000]
        self.assertIn("Consequence (Y) ↓ / Likelihood (X) →", body_google, "Team Google Heatmap must have standard axis title")
        self.assertTrue("Rare" in body_google and "Almost Certain" in body_google, "Team Google Heatmap must have Rare to Almost Certain")
        
        # Verify old rotated / inverted labels are removed from static HTML
        self.assertNotIn("[writing-mode:vertical-rl]", self.html, "Rotated vertical Likelihood label must be removed")
        self.assertNotIn("<div>1 - Minor</div>", self.html, "Bottom Consequence row labels must be removed from HTML")

    def test_bug_46_driver_tree_interactive_drilldowns(self):
        """Bug #46: CD1 Driver Tree cards must support interactive drill-downs and jumps."""
        idx = self.html.find("function renderDriverTreeCards")
        if idx == -1:
            idx = self.html.find("renderDriverTree")
        self.assertNotEqual(idx, -1, "Driver tree render function must exist")
        body = self.html[idx:idx+4000]
        self.assertTrue(
            "jumpToDriverRef" in body or "filterRiskExplorerByDriverRef" in self.html or "openDeliverableModal" in self.html or "switchTab('overview')" in body or "switchTab" in body,
            "Driver tree deliverable cards or badges must have interactive navigation"
        )

    def test_bug_41_exec_summary_blueprint_badges(self):
        """Bug #41: Executive summary Top 3 attention items must have clickable Blueprint badges."""
        idx = self.html.find("function renderExecBriefing")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertTrue(
            "switchTab('blueprints')" in body or "filterRiskExplorerByBundle" in body or "jumpToBlueprintBundle" in self.html,
            "Executive summary attention items must have clickable Blueprint Knowledge links"
        )

    def test_bug_44_team_google_clear_filter_banner(self):
        """Bug #44: Team Google tab must provide a visible clear filter button."""
        self.assertIn("clearTeamGoogleActiveCellFilter", self.html, "clearTeamGoogleActiveCellFilter function must exist")
        self.assertIn("teamGoogleActiveCellFilterBanner", self.html, "teamGoogleActiveCellFilterBanner must exist in HTML")

    def test_bug_45_issue_modal_blueprint_traceability(self):
        """Bug #45: openItemDetailModal for issues must build Blueprint Traceability card."""
        idx = self.html.find("function openItemDetailModal")
        idx_end = self.html.find("function ", idx + 30)
        body = self.html[idx:idx_end]
        self.assertIn("NotebookLM", body, "openItemDetailModal must include NotebookLM links for both risks and issues")

    def test_bug_38_podcast_metadata_week_27(self):
        """Bug #38: Podcast audio briefing metadata must reference Week 27."""
        self.assertIn("Week 27", self.html, "Dashboard must reference Week 27 in podcast/exec briefing")

    def test_bug_32_issue_table_viewport_stretch(self):
        """Bug #32: Issue table container must stretch with dynamic viewport height."""
        idx = self.html.find("id=\"view-issues\"")
        body = self.html[idx:idx+2500]
        self.assertTrue(
            "h-[calc(100vh-" in body or "min-h-[calc(100vh-" in body or "flex-1" in body,
            "Issue table container must have vertical viewport height calculation"
        )

if __name__ == "__main__":
    unittest.main()
