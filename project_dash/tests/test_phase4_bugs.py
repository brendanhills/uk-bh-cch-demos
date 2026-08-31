"""Regression tests for Phase 4 bug fixes."""

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


def test_bug_42_risk_explorer_container_id_aligned(project_root: Path):
    """Bug #42: renderRiskExplorer must update explorerCardsContainer element."""
    html = load_full_html(project_root)
    idx = html.find("function renderRiskExplorer")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "explorerCardsContainer" in body, "renderRiskExplorer must target explorerCardsContainer"
    assert "explorerCardsContainer" in html, "HTML must contain id='explorerCardsContainer'"


def test_bug_39_exec_summary_top_5_populated(project_root: Path):
    """Bug #39: Executive Summary must populate execTopRisksFullList and execTopIssuesFullList."""
    html = load_full_html(project_root)
    assert "execTopRisksFullList" in html, "HTML must contain execTopRisksFullList container"
    assert "execTopIssuesFullList" in html, "HTML must contain execTopIssuesFullList container"

    idx = html.find("function renderExecBriefing")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "renderTop5Risks" in html or "execTopRisksFullList" in body, (
        "renderExecBriefing or dedicated functions must populate top 5 risks"
    )
    assert "renderTop5Issues" in html or "execTopIssuesFullList" in body, (
        "renderExecBriefing or dedicated functions must populate top 5 issues"
    )


def test_bug_40_matrix_axes_standardized_across_both_registers(project_root: Path):
    """Bug #40: Both Joint and Team Google matrices must have X=Likelihood and Y=Consequence."""
    html = load_full_html(project_root)
    # Check Joint matrix renderer
    idx_joint = html.find("function renderRiskHeatmap")
    body_joint = html[idx_joint:idx_joint+2500]
    assert "Rare" in body_joint and "Almost Certain" in body_joint, "Joint Heatmap X-axis must have Rare to Almost Certain"
    assert "Consequence (Y) ↓ / Likelihood (X) →" in body_joint, "Joint Heatmap must have standard axis title"

    # Check Team Google matrix renderer
    idx_google = html.find("function renderTeamGoogleHeatmap")
    body_google = html[idx_google:idx_google+3000]
    assert "Consequence (Y) ↓ / Likelihood (X) →" in body_google, "Team Google Heatmap must have standard axis title"
    assert "Rare" in body_google and "Almost Certain" in body_google, "Team Google Heatmap must have Rare to Almost Certain"

    # Verify old rotated / inverted labels are removed from static HTML
    assert "[writing-mode:vertical-rl]" not in html, "Rotated vertical Likelihood label must be removed"
    assert "<div>1 - Minor</div>" not in html, "Bottom Consequence row labels must be removed from HTML"


def test_bug_46_driver_tree_interactive_drilldowns(project_root: Path):
    """Bug #46: CD1 Driver Tree cards must support interactive drill-downs and jumps."""
    html = load_full_html(project_root)
    idx = html.find("function renderDriverTreeCards")
    if idx == -1:
        idx = html.find("renderDriverTree")
    assert idx != -1, "Driver tree render function must exist"
    body = html[idx:idx+4000]
    assert (
        "jumpToDriverRef" in body or
        "filterRiskExplorerByDriverRef" in html or
        "openDeliverableModal" in html or
        "switchTab('overview')" in body or
        "switchTab" in body
    ), "Driver tree deliverable cards or badges must have interactive navigation"


def test_bug_41_exec_summary_blueprint_badges(project_root: Path):
    """Bug #41: Executive summary Top 3 attention items must have clickable Blueprint badges."""
    html = load_full_html(project_root)
    idx = html.find("function renderExecBriefing")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert (
        "switchTab('blueprints')" in body or
        "filterRiskExplorerByBundle" in body or
        "jumpToBlueprintBundle" in html
    ), "Executive summary attention items must have clickable Blueprint Knowledge links"


def test_bug_44_team_google_clear_filter_banner(project_root: Path):
    """Bug #44: Team Google tab must provide a visible clear filter button."""
    html = load_full_html(project_root)
    assert "clearTeamGoogleActiveCellFilter" in html, "clearTeamGoogleActiveCellFilter function must exist"
    assert "teamGoogleActiveCellFilterBanner" in html, "teamGoogleActiveCellFilterBanner must exist in HTML"


def test_bug_45_issue_modal_blueprint_traceability(project_root: Path):
    """Bug #45: openItemDetailModal for issues must build Blueprint Traceability card."""
    html = load_full_html(project_root)
    idx = html.find("function openItemDetailModal")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "Contract Blueprint Traceability" in body, (
        "openItemDetailModal must render Contract Blueprint Traceability card for issues"
    )