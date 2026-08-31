"""Regression tests for Phase 2 bug fixes."""

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


def test_bug_28_and_35_workspace_sync_modal_4_streams(project_root: Path):
    """Bugs #28 & #35: Workspace Live Sync modal must include Team Google and NotebookLM streams."""
    html = load_full_html(project_root)
    assert 'id="sheetsModal"' in html, "sheetsModal must exist"
    idx = html.find('id="sheetsModal"')
    idx_end = html.find('<!-- SCRIPT CONTROLLERS -->')
    modal_html = html[idx:idx_end]

    # Must include Team Google Sheet link
    assert "1lNRf5NEBd6ygc91nNwFA4HWGFfbDK02QkbkVfr4OUoA" in modal_html, "sheetsModal must link to Team Google Sheet"
    # Must include NotebookLM link
    assert "acdbb29b-8632-4fc7-9ba8-2357beeff141" in modal_html, "sheetsModal must link to NotebookLM"
    # Must include Notebook sync trigger
    assert "triggerNotebookSync" in modal_html or "syncAllWorkspaceSources" in modal_html, (
        "sheetsModal must provide a trigger to sync NotebookLM and all sources"
    )


def test_bug_27_exec_briefing_synthesizes_team_google_and_blueprints(project_root: Path):
    """Bug #27: Executive briefing must synthesize Team Google and Blueprint datasets."""
    html = load_full_html(project_root)
    assert "function renderExecBriefing" in html, "renderExecBriefing must be defined"
    idx = html.find("function renderExecBriefing")
    exec_body = html[idx:idx+4000]

    # Must reference LIVE_TEAM_GOOGLE_RISKS in synthesis or KPIs
    assert "LIVE_TEAM_GOOGLE_RISKS" in exec_body or "teamGoogle" in exec_body or "Team Google" in exec_body, (
        "renderExecBriefing must include Team Google risks in synthesis"
    )
    # Must reference Notebook or Blueprint mappings
    assert (
        "NOTEBOOK_CATALOG" in exec_body or
        "BUNDLE_ANNEX_MAPPING" in exec_body or
        "Blueprint" in exec_body or
        "NotebookLM" in exec_body
    ), "renderExecBriefing must link or reference contract blueprint intelligence"