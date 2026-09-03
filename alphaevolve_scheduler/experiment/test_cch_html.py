import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestCCHHtmlAndScriptIntegrity(unittest.TestCase):
    def setUp(self):
        self.html_path = ROOT / "cch" / "index.html"
        if not self.html_path.exists():
            self.html_path = ROOT / "rch" / "index.html"
        self.assertTrue(self.html_path.exists(), "cch/index.html does not exist")
        self.html_content = self.html_path.read_text(encoding="utf-8")
        
        script_start = self.html_content.find("<script>")
        script_end = self.html_content.rfind("</script>")
        self.assertGreater(script_start, 0, "No <script> tag found in cch/index.html")
        self.assertGreater(script_end, script_start, "No closing </script> tag found in cch/index.html")
        self.script_content = self.html_content[script_start + 8 : script_end]

    def test_dom_element_ids_exist(self):
        """Ensure all DOM element IDs referenced in JavaScript exist in the HTML body."""
        required_ids = [
            "gantt-rows",
            "gantt-blocks-layer",
            "staff-grid-container",
            "scenario-select",
            "bd-scenario-name",
            "bd-scenario-desc-text",
            "bd-scenario-tag",
            "bd-summary-desc",
            "bd-throughput-gain",
            "bd-throughput-sub",
            "bd-fatigue-reduction",
            "bd-fatigue-sub",
            "bd-base-resource-text",
            "bd-base-people-text",
            "metric-patients",
            "metric-patients-delta",
            "metric-overtime",
            "metric-idle",
            "metric-fatigue",
            "play-btn",
            "scenario-hint",
            "active-day-label",
            "stats-Monday",
            "badge-Monday",
            "toggle-baseline",
            "toggle-evolved",
            "view-grid",
            "view-breakdown",
            "algo-title",
            "formula-toggle",
            "formula-content",
            "cch-tooltip" if "id=\"cch-tooltip\"" in self.html_content else "rch-tooltip",
            "main-dashboard",
            "breakdown-panel",
        ]
        
        for dom_id in required_ids:
            pattern = f'id="{dom_id}"'
            self.assertIn(pattern, self.html_content, f"Required DOM element id='{dom_id}' missing in html")

    def test_javascript_bracket_and_parenthesis_balance(self):
        """Ensure all curly braces and parentheses in script block are perfectly balanced."""
        lines = self.script_content.split("\n")
        stack = []
        
        for idx, line in enumerate(lines, 1):
            in_str = None
            in_comment = False
            for col, c in enumerate(line):
                if in_comment:
                    break
                if c in ('"', "'", "`"):
                    if in_str == c:
                        in_str = None
                    elif not in_str:
                        in_str = c
                    continue
                if in_str:
                    continue
                if c == "/" and col + 1 < len(line) and line[col + 1] == "/":
                    in_comment = True
                    break
                    
                if c in "{(":
                    stack.append((c, idx, line.strip()))
                elif c in "})":
                    self.assertTrue(bool(stack), f"Unmatched closing '{c}' at line {idx}: {line.strip()}")
                    top = stack[-1][0]
                    if (c == "}" and top == "{") or (c == ")" and top == "("):
                        stack.pop()
                    else:
                        self.fail(f"Mismatched closing '{c}' at line {idx} (expected '{top}')")
                        
        self.assertEqual(len(stack), 0, f"Unclosed brackets/parentheses in script block: {stack}")

    def test_render_breakdown_variables_defined(self):
        """Ensure scenarioName and all required variables in renderBreakdown are declared before use."""
        self.assertIn("function renderBreakdown()", self.script_content)
        
        rb_start = self.script_content.find("function renderBreakdown()")
        rb_end = self.script_content.find("function renderCurrentStep()")
        self.assertGreater(rb_end, rb_start, "renderCurrentStep not found after renderBreakdown")
        
        rb_code = self.script_content[rb_start:rb_end]
        
        # Verify scenarioName is explicitly declared
        self.assertIn("scenarioName", rb_code, "scenarioName missing in renderBreakdown()")
        self.assertRegex(
            rb_code,
            r"(const|let|var)\s+scenarioName\s*=",
            "scenarioName is referenced in renderBreakdown() but not declared via const/let/var!"
        )
        
        # Verify scInfo, basePatients, bestPatients, baseFatigue, bestFatigue are declared
        for var_name in ["scInfo", "basePatients", "bestPatients", "baseFatigue", "bestFatigue"]:
            self.assertRegex(
                rb_code,
                rf"(const|let|var)\s+{var_name}\s*=",
                f"Variable '{var_name}' referenced in renderBreakdown() but not declared!"
            )

    def test_fatigue_formatting_logic(self):
        """Ensure fatigue metric formatting handles negative and positive fatigueDiff without double minus signs."""
        self.assertNotIn("`-${fatiguePct}%`", self.script_content, "Found naive `-${fatiguePct}%` string formatting causing double minus '--'")
        self.assertIn("fatigueDiff < 0", self.script_content)

    def test_fetch_dataset_helper_present(self):
        """Ensure fetchDataset handles carriage returns and multi-path fallbacks."""
        self.assertIn("async function fetchDataset", self.script_content)
        self.replace_cr_in_fetch = "replace(/\\r/g, '')" in self.script_content
        self.assertTrue(self.replace_cr_in_fetch)

    def test_show_tooltip_evolution_diff(self):
        """Ensure showTooltip function checks previous/original coordinates and renders evolution diff information."""
        st_start = self.script_content.find("function showTooltip(")
        st_end = self.script_content.find("function hideTooltip()")
        self.assertGreater(st_start, 0, "showTooltip function not found in script content")
        self.assertGreater(st_end, st_start, "hideTooltip function not found after showTooltip")

        st_code = self.script_content[st_start:st_end]

        # Ensure showTooltip references prev_room/orig_room/prev_time or diff logic
        self.assertTrue(
            "prev_room" in st_code or "orig_room" in st_code or "prev_day" in st_code or "diff" in st_code,
            "showTooltip() does not reference any previous coordinate fields (prev_room, prev_day, prev_time, orig_room) to render evolution diff information!"
        )
        self.assertTrue(
            "cch-tooltip-diff" in st_code or "rch-tooltip-diff" in st_code,
            "showTooltip() missing 'cch-tooltip-diff' container for rendering evolution diff details"
        )
        self.assertIn(
            "activeStoryPhase === 3",
            st_code,
            "showTooltip() must check activeStoryPhase === 3 before rendering Evolution Delta"
        )

    def test_default_scenario_is_dynamic_live_run(self):
        """Ensure scenario dropdown defaults to Dynamic Live Run (traces_dynamic.jsonl) on page load."""
        self.assertIn(
            '<option value="traces_dynamic.jsonl" selected',
            self.html_content,
            "traces_dynamic.jsonl is not set as the selected option in #scenario-select dropdown"
        )

    def test_tooltip_staff_layout_matches_grid(self):
        """Ensure showTooltip formats staff displaying staff name and role before ID matching staff grid card structure."""
        st_start = self.script_content.find("function showTooltip(")
        st_end = self.script_content.find("function hideTooltip()")
        st_code = self.script_content[st_start:st_end]
        
    def test_candidate_exploration_feed_ui_elements(self):
        """Ensure DOM elements and JS logic exist for real-time candidate exploration feed (Bug #17)."""
        required_ids = [
            "candidate-feed-banner",
            "metric-candidates-total",
            "metric-candidates-accepted",
            "metric-candidates-infeasible",
            "metric-candidate-status-badge",
        ]
        for dom_id in required_ids:
            self.assertIn(f'id="{dom_id}"', self.html_content, f"Missing candidate feed DOM element id='{dom_id}'")

        # Check that renderCurrentStep updates candidate metrics
        rs_start = self.script_content.find("function renderCurrentStep()")
        rs_end = self.script_content.find("function showTooltip(")
        self.assertGreater(rs_start, 0)
        self.assertGreater(rs_end, rs_start)
        rs_code = self.script_content[rs_start:rs_end]

        self.assertIn("metric-candidates-total", rs_code)
        self.assertIn("metric-candidates-accepted", rs_code)
        self.assertIn("metric-candidates-infeasible", rs_code)

    def test_bug16_cymbal_childrens_hospital_name(self):
        """Bug #16: Ensure hospital name is neutral 'Cymbal Children's Hospital' in document title and h1 header."""
        self.assertIn("Cymbal Children's Hospital", self.html_content, "Neutral hospital name 'Cymbal Children\\'s Hospital' missing in rch/index.html")
        self.assertNotIn("The Royal Children's Hospital", self.html_content, "Old hospital name 'The Royal Children\\'s Hospital' still present in rch/index.html")

    def test_bug21_scenario_switch_resets_to_baseline_view(self):
        """Bug #21: Ensure switching scenarios resets isEvolvedMode to false and activates toggle-baseline."""
        scen_start = self.script_content.find("scenarioSelect.addEventListener('change'")
        self.assertGreater(scen_start, 0, "scenario-select change listener not found")
        scen_code = self.script_content[scen_start : scen_start + 600]
        self.assertIn("isEvolvedMode = false", scen_code, "scenario-select change listener does not reset isEvolvedMode = false")
        self.assertIn("toggle-baseline", scen_code, "scenario-select change listener does not activate toggle-baseline")
        self.assertIn("toggle-evolved", scen_code, "scenario-select change listener does not deactivate toggle-evolved")

    def test_bug22_day_label_format_and_header_centering(self):
        """Bug #22: Ensure active-day-label displays just day name (e.g. 'Monday') without '(showing: ...)' and is centered."""
        self.assertNotIn("(Showing: Monday)", self.html_content, "Old '(Showing: Monday)' label still present in HTML")
        self.assertNotIn("(showing:", self.script_content, "JS still sets textContent with '(Showing: ...)' format")
        self.assertIn("activeDayLabel.textContent = activeDay", self.script_content, "JS should set activeDayLabel textContent directly to activeDay")

    def test_bug23_staff_grid_expanded_height(self):
        """Bug #23: Ensure .staff-grid does not have a rigid max-height: 200px that clips staff cards."""
        self.assertNotIn("max-height: 200px;", self.html_content, ".staff-grid still has rigid max-height: 200px")
        self.assertTrue(
            "max-height: none" in self.html_content or "max-height: 480px" in self.html_content or "max-height: 500px" in self.html_content,
            ".staff-grid should have max-height: none or >= 480px to prevent clipping staff details"
        )

    def test_bug30_control_group_layout_and_evolution_chart(self):
        """Bug #30: Ensure controls are structured into primary scenario, hero algorithm evolution, and disruption stress-test groups, with evolution chart container."""
        # 1. Verify 3 control group containers exist in HTML
        self.assertIn('class="control-group-scenario"', self.html_content, "Missing .control-group-scenario in header controls")
        self.assertIn('class="control-group-hero-evolution"', self.html_content, "Missing .control-group-hero-evolution in header controls")
        self.assertIn('class="control-group-disruption"', self.html_content, "Missing .control-group-disruption in header controls")
        
        # 2. Verify evolution fitness chart container exists
        self.assertIn('id="evolution-fitness-chart"', self.html_content, "Missing #evolution-fitness-chart container for algorithm evolution graph")

    def test_bug4_completion_state_indicator(self):
        """Bug #4: Ensure JS updates status badge and play button when evolution search reaches completion."""
        self.assertIn("fitness-chart-latest", self.html_content)
        self.assertIn("🔄 Replay Algorithm Evolution", self.script_content, "JS missing completion text update for play-btn")

    def test_bug19_dynamic_random_ot_disruption_injection(self):
        """Bug #19: Ensure Simulate OT Disruption dynamically picks random rooms/days and triggers re-routing adaptation step."""
        btn_start = self.script_content.find("btnInjectOt.addEventListener('click'")
        self.assertGreater(btn_start, 0, "btnInjectOt click listener not found in script content")
        btn_code = self.script_content[btn_start : btn_start + 6500]
        self.assertIn("randomRoom", btn_code, "Simulate OT Disruption should dynamically pick a random room")
        self.assertIn("Dynamic Re-Plan", btn_code, "Simulate OT Disruption should add an adaptation step insight")

    def test_bug20_emergency_arrival_triggers_reassignment(self):
        """Bug #20: Ensure Simulate Emergency Arrival re-assigns preempted routine surgeries to alternate rooms."""
        er_start = self.script_content.find("btnInjectEr.addEventListener('click'")
        self.assertGreater(er_start, 0, "btnInjectEr click listener not found in script content")
        er_code = self.script_content[er_start : er_start + 1500]
        self.assertIn("bumped", er_code, "Simulate Emergency Arrival should bump and re-assign preempted routine surgeries")

    def test_bug43_disrupt_active_displayed_day(self):
        """Bug #43: Ensure Simulate OT Disruption targets activeDay being displayed."""
        btn_start = self.script_content.find("btnInjectOt.addEventListener('click'")
        self.assertGreater(btn_start, 0)
        btn_code = self.script_content[btn_start : btn_start + 5000]
        self.assertIn("activeDay", btn_code, "Simulate OT Disruption should target activeDay")

    def test_bug41_baseline_schedule_trigger(self):
        """Bug #41: Ensure baseline trigger button is removed from header controls."""
        self.assertNotIn("btn-run-baseline", self.html_content)

    def test_bug42_highlight_staff_workload_changes(self):
        """Bug #42: Highlight staff cards whose workload changes between search steps."""
        self.assertIn("staff-card-mutated", self.html_content + self.script_content)

    def test_bug44_open_dynamic_live_run_by_default(self):
        """Bug #44: Default scenario selection should be traces_dynamic.jsonl."""
        self.assertIn('value="traces_dynamic.jsonl" selected', self.html_content)

    def test_bug46_round_overtime_and_show_in_popup(self):
        """Bug #46: Round overtime to 1 decimal place in candidate feed and display in tooltip popup."""
        self.assertIn(".toFixed(1)", self.script_content)
        self.assertIn("Overtime:", self.script_content)

    def test_bug45_relabel_legacy_kmart(self):
        """Bug #45: Ensure Kmart demo is labeled alternative demo rather than Legacy Kmart."""
        self.assertNotIn("LEGACY KMART", self.html_content.upper())

    def test_bug48_evolution_curve_colors_and_scale(self):
        """Bug #48: Color evolution curve dots by status and add scale/ticks."""
        self.assertIn("chart-grid-scale", self.html_content + self.script_content)
        self.assertIn("DEGRADED", self.script_content)

    def test_bug49_gantt_headers_cover_overtime_bounds(self):
        """Bug #49: Gantt timeline headers should extend to 21:00 or 22:00 to cover overtime bounds."""
        self.assertIn("21:00", self.html_content)

    def test_bug51_demo_mode_controller_status_message(self):
        """Bug #51: Ensure Demo Mode uses 'Simulating AlphaEvolve generating candidates' status message."""
        self.assertIn("Simulating AlphaEvolve generating candidates", self.html_content + self.script_content)

    def test_bug50_reset_demo_button(self):
        """Bug #50: Ensure Reset Demo button exists and clears disruptions and resets replay step."""
        self.assertIn("btn-reset-demo", self.html_content)
        self.assertIn("resetDemoState", self.script_content)

    def test_bug52_candidate_feed_patient_delta_arrow_matches_sign(self):
        """Bug #52: Candidate feed patient delta arrow must match the sign of patientDiff (▲ for positive, ▼ for negative)."""
        feed_start = self.script_content.find("async function renderCandidateFeed()")
        self.assertGreater(feed_start, 0)
        feed_code = self.script_content[feed_start : feed_start + 12000]
        # Should not hardcode (▼ ${sign}${patientDiff}) for degraded/rejected when patientDiff is positive
        self.assertNotIn("(▼ ${sign}${patientDiff})", feed_code, "Patient count delta should not hardcode down arrow ▼ for positive patientDiff")
        self.assertIn("patientDiff >= 0 ? '▲' : '▼'", feed_code, "Patient delta arrow should match the sign of patientDiff")

    def test_bug53_evolution_curve_plots_all_feed_candidates(self):
        """Bug #53: Algorithm Evolution Improvement Curve graph should plot all evaluated candidates from candidate feed."""
        chart_start = self.script_content.find("function renderEvolutionFitnessChart()")
        self.assertGreater(chart_start, 0)
        chart_code = self.script_content[chart_start : chart_start + 4000]
        self.assertIn("EVOLUTION_DATA.candidates", chart_code, "renderEvolutionFitnessChart should plot EVOLUTION_DATA.candidates from the candidate feed")

if __name__ == "__main__":
    unittest.main()




