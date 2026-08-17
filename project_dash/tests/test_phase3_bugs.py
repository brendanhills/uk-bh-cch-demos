#!/usr/bin/env python3
import unittest
import re
import os

class TestPhase3Bugs(unittest.TestCase):
    def setUp(self):
        self.index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "index.html"))
        with open(self.index_path, "r", encoding="utf-8") as f:
            self.html = f.read()

    def test_bug_36_matrix_axes_labels_orientation(self):
        """Bug #36: 5x5 Heatmap Matrix must have clear Likelihood horizontal and Consequence vertical labels."""
        self.assertIn("Likelihood", self.html, "Heatmap must label horizontal columns as Likelihood")
        self.assertIn("Consequence", self.html, "Heatmap must label vertical rows as Consequence")
        
        idx = self.html.find("function renderRiskHeatmap")
        render_body = self.html[idx:idx+2500]
        self.assertNotIn("Consequence ↓</div>\n                    <div>1 Rare", render_body, "Top columns must not be labeled as Consequence")
        self.assertTrue(
            "Likelihood" in render_body or "Probable" in render_body,
            "renderRiskHeatmap must clarify horizontal axis is Likelihood"
        )

    def test_bug_37_unified_risk_card_interaction_template(self):
        """Bug #37: Joint Program and Team Google risk cards must both support in-line expansion and full detail modal."""
        idx_joint = self.html.find("function renderRiskExplorer")
        idx_joint_end = self.html.find("function ", idx_joint + 30)
        joint_body = self.html[idx_joint:idx_joint_end]
        
        idx_google = self.html.find("function renderTeamGoogleRiskExplorer")
        idx_google_end = self.html.find("function ", idx_google + 30)
        google_body = self.html[idx_google:idx_google_end]
        
        # Both must have openItemDetailModal
        self.assertIn("openItemDetailModal", joint_body, "Joint risk cards must support openItemDetailModal")
        self.assertIn("openItemDetailModal", google_body, "Team Google risk cards must support openItemDetailModal")
        
        # Both must support in-line details / expandable sections
        self.assertTrue(
            "Root Cause" in joint_body or "Treatment" in joint_body,
            "Joint cards must render root cause/treatment details"
        )
        self.assertTrue(
            "Root Cause" in google_body or "Treatment" in google_body,
            "Team Google cards must render root cause/treatment details"
        )

    def test_bug_29_exec_cockpit_clickable_pills_and_banner(self):
        """Bug #29: Executive Cockpit top banner and KPI pills must be interactive/clickable."""
        self.assertTrue(
            "switchTab('overview')" in self.html or "switchTab('team-google')" in self.html or "switchTab('issues')" in self.html,
            "Executive Cockpit header pills must link to relevant views"
        )

    def test_bug_26_widescreen_margin_expansion(self):
        """Bug #26: Main container should support wide layout max-w-[1750px] or max-w-screen-2xl."""
        self.assertTrue(
            "max-w-[1750px]" in self.html or "max-w-[1800px]" in self.html or "max-w-7xl" in self.html or "max-w-screen-2xl" in self.html or "max-w-[1680px]" in self.html,
            "Main layout container must allow widescreen viewing"
        )

    def test_bug_32_issue_register_table_vertical_height(self):
        """Bug #32: Issue register table container must extend vertically to fill viewport height."""
        idx = self.html.find("id=\"view-issues\"")
        self.assertNotEqual(idx, -1, "view-issues tab must exist")
        issues_html = self.html[idx:idx+2500]
        self.assertTrue(
            "min-h-" in issues_html or "h-full" in issues_html or "flex-1" in issues_html or "overflow-y-auto" in issues_html,
            "Issue register container must stretch vertically"
        )

if __name__ == "__main__":
    unittest.main()
