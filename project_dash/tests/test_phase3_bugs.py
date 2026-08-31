"""Regression tests for Phase 3 bug fixes."""

from pathlib import Path
import pytest


def load_full_html(project_root: Path) -> str:
    """Loads index.html concatenated with all ES modules under src/js/."""
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    js_dir = project_root / 'src' / 'js'
    if js_dir.exists():
        for fn in sorted(js_dir.rglob('*.js')):
            html += '\n' + fn.read_text(encoding='utf-8')
    return html


def test_bug_36_matrix_axes_labels_orientation(project_root: Path):
    """Bug #36: 5x5 Heatmap Matrix must have clear Likelihood horizontal and Consequence vertical labels."""
    html = load_full_html(project_root)
    assert "Likelihood" in html, "Heatmap must label horizontal columns as Likelihood"
    assert "Consequence" in html, "Heatmap must label vertical rows as Consequence"

    idx = html.find("function renderRiskHeatmap")
    render_body = html[idx:idx+2500]
    assert "Consequence ↓</div>\n                    <div>1 Rare" not in render_body, "Top columns must not be labeled as Consequence"
    assert "Likelihood" in render_body or "Probable" in render_body, "renderRiskHeatmap must clarify horizontal axis is Likelihood"


def test_bug_37_unified_risk_card_interaction_template(project_root: Path):
    """Bug #37: Joint Program and Team Google risk cards must both support in-line expansion and full detail modal."""
    html = load_full_html(project_root)
    idx_joint = html.find("function renderRiskExplorer")
    idx_joint_end = html.find("function ", idx_joint + 30)
    joint_body = html[idx_joint:idx_joint_end]

    idx_google = html.find("function renderTeamGoogleRiskExplorer")
    idx_google_end = html.find("function ", idx_google + 30)
    google_body = html[idx_google:idx_google_end]

    # Both must have openItemDetailModal
    assert "openItemDetailModal" in joint_body, "Joint risk cards must support openItemDetailModal"
    assert "openItemDetailModal" in google_body, "Team Google risk cards must support openItemDetailModal"

    # Both must support in-line details / expandable sections
    assert "Root Cause" in joint_body or "Treatment" in joint_body, "Joint cards must render root cause/treatment details"
    assert "Root Cause" in google_body or "Treatment" in google_body, "Team Google cards must render root cause/treatment details"


def test_bug_29_exec_cockpit_clickable_pills_and_banner(project_root: Path):
    """Bug #29: Executive Cockpit top banner and KPI pills must be interactive/clickable."""
    html = load_full_html(project_root)
    assert (
        "switchTab('overview')" in html or
        "switchTab('team-google')" in html or
        "switchTab('issues')" in html
    ), "Executive Cockpit header pills must link to relevant views"


def test_bug_26_widescreen_margin_expansion(project_root: Path):
    """Bug #26: Main container should support wide layout max-w-[1750px] or max-w-screen-2xl."""
    html = load_full_html(project_root)
    assert (
        "max-w-[1750px]" in html or
        "max-w-[1800px]" in html or
        "max-w-7xl" in html or
        "max-w-screen-2xl" in html or
        "max-w-[1680px]" in html
    ), "Main layout container must allow widescreen viewing"


def test_bug_32_issue_register_table_vertical_height(project_root: Path):
    """Bug #32: Issue register table container must extend vertically to fill viewport height."""
    html = load_full_html(project_root)
    idx = html.find('id="view-issues"')
    assert idx != -1, "view-issues tab must exist"
    issues_html = html[idx:idx+2500]
    assert (
        "min-h-" in issues_html or
        "h-full" in issues_html or
        "flex-1" in issues_html or
        "overflow-y-auto" in issues_html
    ), "Issue register container must stretch vertically"