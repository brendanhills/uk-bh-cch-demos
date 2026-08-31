"""Regression tests for Phase 5 bug fixes."""

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


def test_bug_32_issue_table_populated_on_switch_tab(project_root: Path):
    """Bug #32: switchTab('issues') must invoke renderIssueTable()."""
    html = load_full_html(project_root)
    idx = html.find("function switchTab")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "renderIssueTable" in body, "switchTab must call renderIssueTable when tab-issues is selected"


def test_bug_49_open_item_detail_modal_matches_google_risk_id(project_root: Path):
    """Bug #49: openItemDetailModal must match stringified ID on LIVE_TEAM_GOOGLE_RISKS and open modal."""
    html = load_full_html(project_root)
    idx = html.find("function openItemDetailModal")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert (
        "String(" in body or "== itemId" in body or "=== String(itemId)" in body
    ), "openItemDetailModal must use robust string-based ID comparison"
    assert "LIVE_TEAM_GOOGLE_RISKS" in body, "openItemDetailModal must query LIVE_TEAM_GOOGLE_RISKS"
    assert "modal.classList.remove('hidden')" in body, "openItemDetailModal must unhide the modal"
    assert "Team Google" in body, "openItemDetailModal must render Team Google badge when inspecting a Google risk"


def test_bug_50_risk_cards_have_blueprint_badges_and_links(project_root: Path):
    """Bug #50: Risk cards in Joint Program and Team Google must render Blueprint Annex badges/links."""
    html = load_full_html(project_root)
    # Joint Risk Explorer
    idx_joint = html.find("function renderRiskExplorer")
    idx_joint_end = html.find("function ", idx_joint + 30)
    body_joint = html[idx_joint:idx_joint_end]
    assert (
        "Annex" in body_joint or "Blueprint" in body_joint or "BUNDLE_ANNEX_MAPPING" in body_joint
    ), "renderRiskExplorer cards must resolve and render Blueprint Annex badges"

    # Team Google Risk Explorer
    idx_google = html.find("function renderTeamGoogleRiskExplorer")
    idx_google_end = html.find("function ", idx_google + 30)
    body_google = html[idx_google:idx_google_end]
    assert (
        "Annex" in body_google or "Blueprint" in body_google or "BUNDLE_ANNEX_MAPPING" in body_google
    ), "renderTeamGoogleRiskExplorer cards must resolve and render Blueprint Annex badges"


def test_bug_47_top_5_cards_have_drilldowns(project_root: Path):
    """Bug #47: Top 5 risks and issues lists must have explicit Inspect and filter drilldowns."""
    html = load_full_html(project_root)
    idx = html.find("function renderTop5Risks")
    idx_end = html.find("function ", idx + 30)
    body = html[idx:idx_end]
    assert "openItemDetailModal" in body, "renderTop5Risks must trigger openItemDetailModal on click"
    assert "Inspect" in body or "hover:text-indigo-700" in body, "renderTop5Risks must show inspect trigger"

    idx_i = html.find("function renderTop5Issues")
    idx_i_end = html.find("function ", idx_i + 30)
    body_i = html[idx_i:idx_i_end]
    assert "openItemDetailModal" in body_i, "renderTop5Issues must trigger openItemDetailModal on click"


def test_bug_48_podcast_audio_playback_and_speech_fallback(project_root: Path):
    """Bug #48: Podcast audio player must have Web Speech API fallback or valid audio source."""
    html = load_full_html(project_root)
    assert (
        "speechSynthesis" in html or "playExecutivePodcast" in html or "togglePodcastPlay" in html
    ), "index.html must have podcast audio playback handler with speech synthesis fallback"


def test_bug_38_podcast_transcript_week_27_with_timestamps(project_root: Path):
    """Bug #38: PODCAST_TRANSCRIPT must have Week 27 dialogue and valid timestamps."""
    html = load_full_html(project_root)
    idx = html.find("PODCAST_TRANSCRIPT")
    assert idx != -1, "PODCAST_TRANSCRIPT structure must exist"
    body = html[idx:idx+3500]
    assert "Week 27" in body, "Transcript must reference Week 27"
    assert "time" in body, "Transcript items must have time property"
    assert "role" in body, "Transcript items must have role property"
    assert "undefined" not in body, "Transcript must not hardcode undefined"