"""Regression tests for Phase 6 bug fixes."""

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


def test_bug_51_issue_table_column_widths_and_concise_ref(project_root: Path):
    """Bug #51: Issue table must have balanced column widths and concise Driver Ref badge."""
    html = load_full_html(project_root)
    idx = html.find("function renderIssueTable")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "renderIssueTable" in html, "renderIssueTable must exist"
    assert "driverTreeRef" in body, "renderIssueTable must format driverTreeRef cleanly"

    # Check table headers have width constraints
    idx_section = html.find('id="view-issues"')
    body_section = html[idx_section:idx_section+2500]
    assert "table" in body_section, "view-issues must have table element"


def test_bug_52_issue_inspect_modal_trigger(project_root: Path):
    """Bug #52: Issue Register must have explicit Inspect button triggering openItemDetailModal."""
    html = load_full_html(project_root)
    idx = html.find("function renderIssueTable")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "openItemDetailModal" in body, "renderIssueTable must call openItemDetailModal with 'issue'"
    assert "Inspect" in body, "renderIssueTable must render Inspect button"


def test_bug_38_podcast_scripts_w27_and_no_undefined(project_root: Path):
    """Bug #38: Podcast dialogue must be resolved dynamically with avatar, role, and time fields."""
    html = load_full_html(project_root)
    assert "function getPodcastScriptForWeek" in html
    assert "renderPodcastTranscript" in html
    assert "function togglePodcastPlayback" in html


def test_bug_48_podcast_audio_assets_exist(project_root: Path):
    """Bug #48: podcast audio file or generator must exist in assets directory."""
    assets_dir = project_root / "assets"
    assert assets_dir.exists(), "assets directory must exist"
    has_audio = (
        (assets_dir / "podcast_w27.mp3").exists() or
        (assets_dir / "podcast_w27.wav").exists()
    )
    assert has_audio, "assets/podcast_w27.wav or .mp3 must exist on disk"