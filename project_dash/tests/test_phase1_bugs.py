"""Regression tests for Phase 1 bug fixes."""

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


def test_bug_30_matrix_cell_click_clears_stale_search(project_root: Path):
    """Bug #30: Clicking a 5x5 heatmap cell must clear conflicting search text."""
    html = load_full_html(project_root)
    assert "function highlightHeatmapCell" in html, "highlightHeatmapCell must be defined"
    idx = html.find("function highlightHeatmapCell")
    idx_end = html.find("function initApp", idx)
    body = html[idx:idx_end] if idx_end != -1 else html[idx:idx+2500]
    assert "explorerSearchInput" in body and ("value = ''" in body or "value=''" in body), (
        "highlightHeatmapCell must reset explorerSearchInput so stale text does not filter out cell risks"
    )


def test_bug_33_blueprint_bundle_filter_matches_mapped_risks(project_root: Path):
    """Bug #33: Blueprint bundle filter must filter risks using BUNDLE_ANNEX_MAPPING."""
    html = load_full_html(project_root)
    assert "function filterRiskExplorerByBundle" in html, "filterRiskExplorerByBundle must be defined"
    idx = html.find("function renderRiskExplorer")
    idx_end = html.find("function renderMatrix", idx)
    render_body = html[idx:idx_end] if idx_end != -1 else html[idx:idx+4000]
    assert "BUNDLE_ANNEX_MAPPING" in render_body and ("jointRisks" in render_body or "activeJointRiskCount" in render_body), (
        "renderRiskExplorer must evaluate bundle membership via BUNDLE_ANNEX_MAPPING or bundle tags"
    )


def test_bug_34_team_google_cards_have_click_drilldown(project_root: Path):
    """Bug #34: Team Google Risk Explorer cards must support click-to-drill-down / modal inspection."""
    html = load_full_html(project_root)
    assert "renderTeamGoogleRiskExplorer" in html, "renderTeamGoogleRiskExplorer must be defined"
    idx = html.find("function renderTeamGoogleRiskExplorer")
    idx_end = html.find("function initApp", idx)
    tg_body = html[idx:idx_end] if idx_end != -1 else html[idx:idx+5000]
    assert "openItemDetailModal" in tg_body, (
        "Team Google risk cards in renderTeamGoogleRiskExplorer must have openItemDetailModal click handler"
    )


def test_bug_31_team_google_matrix_standardized_layout(project_root: Path):
    """Bug #31: Team Google 5x5 heatmap must follow the standardized 5x5 matrix layout."""
    html = load_full_html(project_root)
    assert "renderTeamGoogleHeatmap" in html, "renderTeamGoogleHeatmap must be defined"
    idx = html.find("function renderTeamGoogleHeatmap")
    idx_end = html.find("function initApp", idx)
    tg_body = html[idx:idx_end] if idx_end != -1 else html[idx:idx+5000]
    assert "filterTeamGoogleMatrixCell" in tg_body or "teamGoogleActiveMatrixCellFilter" in tg_body, (
        "Team Google heatmap cells must have interactive cell click filtering"
    )