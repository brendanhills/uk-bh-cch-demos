"""Stability and data integrity regression tests for Phase 1 enhancements."""

import json
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


@pytest.fixture(scope="module")
def html_content(project_root: Path) -> str:
    return load_full_html(project_root)


def test_fdse_data_files_exist_and_valid(project_root: Path):
    """Verify all F-DSE project raw data files exist and parse as valid JSON."""
    fdse_dir = project_root / 'data' / 'f-dse'
    required_files = [
        'config.json', 'risks.json', 'issues.json', 'snapshots.json',
        'driver_tree.json', 'knowledge.json'
    ]
    for filename in required_files:
        file_path = fdse_dir / filename
        assert file_path.exists(), f"Missing data file: {filename}"
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data is not None


def test_fdse_knowledge_sources_has_annexes(project_root: Path):
    """Verify F-DSE knowledge.json contains solution blueprint annexes."""
    k_file = project_root / 'data' / 'f-dse' / 'knowledge.json'
    with open(k_file, 'r', encoding='utf-8') as f:
        k = json.load(f)

    sources = k.get('sources', [])
    blueprints = [s for s in sources if s.get('bundle')]
    assert len(blueprints) >= 10, "Expected at least 10 blueprint bundle sources in F-DSE knowledge"


def test_driver_tree_normalization_in_html(html_content: str):
    """Verify index.html normalizes description, completeBy, and progress."""
    assert "description: g.description || g.name || g.title" in html_content
    assert "completeBy: g.completeBy || g.dueDate || g.targetDate" in html_content
    assert "progress: g.progress !== undefined ? g.progress" in html_content


def test_dynamic_timeline_metrics_in_html(html_content: str):
    """Verify computeTimelineMetrics computes dynamically across snapshots."""
    assert "function computeTimelineMetrics(granularity)" in html_content
    assert "PRECOMPUTED_ANALYTICS" not in html_content


def test_top5_resilience_in_html(html_content: str):
    """Verify renderTop5Risks and renderTop5Issues have name fallbacks and empty states."""
    assert "r.riskName || r.riskTitle || r.riskDescription || r.title" in html_content
    assert "i.issueName || i.issueTitle || i.issueDescription" in html_content
    assert "No active risks recorded" in html_content
    assert "No active escalated issues recorded" in html_content


def test_team_google_status_filter_clears_matrix_cell(html_content: str):
    """Verify setTeamGoogleStatusFilter resets active matrix cell filter."""
    assert "teamGoogleActiveMatrixCellFilter = null;" in html_content


def test_header_controls_flex_nowrap_and_no_dropdown(html_content: str):
    """Verify header action bar has flex-nowrap and dropdown is removed."""
    assert "flex items-center gap-2 flex-nowrap shrink-0" in html_content
    assert 'id="projectDropdownMenu"' not in html_content
    assert "data:image/svg+xml," in html_content


def test_podcast_script_resolution_and_speech_synthesis(html_content: str):
    """Verify getPodcastScriptForWeek is called for rendering, copying, and speaking podcast."""
    assert "const script = getPodcastScriptForWeek(activeTimeMachineWeek);" in html_content
    assert "window.speechSynthesis.speak(utterance);" in html_content
    assert "function toggleTranscriptModal()" in html_content


def test_fdse_driver_tree_has_24_gates_and_levels(project_root: Path):
    """Verify F-DSE driver_tree.json contains all 24 gates and both L2/L3 levels (Bug #70)."""
    dt_file = project_root / 'data' / 'f-dse' / 'driver_tree.json'
    with open(dt_file, 'r', encoding='utf-8') as f:
        dt = json.load(f)

    all_gates = []
    for cd in dt.get('capabilityDrops', []):
        all_gates.extend(cd.get('gates', []))

    assert len(all_gates) == 24, "Expected exactly 24 contractual capability drop gates"
    l2_gates = [g for g in all_gates if g.get('level') == 2]
    l3_gates = [g for g in all_gates if g.get('level') == 3]
    assert len(l2_gates) >= 10, "Expected at least 10 Level 2 Primary Gates"
    assert len(l3_gates) >= 10, "Expected at least 10 Level 3 Work Packages"


def test_header_dual_sheet_dropdown(html_content: str):
    """Verify header action bar has dual Google Sheets dropdown (Bug #56)."""
    assert 'id="sheetDropdownWrapper"' in html_content
    assert 'id="headerJointSheetLink"' in html_content
    assert 'id="headerTeamGoogleSheetLink"' in html_content
    assert "function toggleSheetDropdown" in html_content


def test_sleeper_outlier_conditional_hide(html_content: str):
    """Verify sleeper outlier hides container when empty and normalizes properties (Bug #71)."""
    assert "slContainer.classList.add('hidden');" in html_content
    assert "sl.risk || sl.description || sl.title" in html_content
    assert "sl.trigger || sl.triggerCondition || sl.action" in html_content


def test_gap_close_plan_id_and_jump(html_content: str):
    """Verify gap close plan cards have unique IDs and jumpToGapClose handles direct lookup (Bug #53)."""
    assert 'id="gapPlan_${g.num}"' in html_content
    assert "document.getElementById(`gapPlan_${cleanNum}`)" in html_content
    assert "↑ Briefing" in html_content
    assert "jumpToGapClose('${gapNum}')" in html_content


def test_podcast_studio_audio_asset_and_priority(project_root: Path, html_content: str):
    """Verify authentic natural audio files exist and audio element is prioritized (Bug #72)."""
    w27_mp3 = project_root / 'assets' / 'podcast_w27.mp3'
    assert w27_mp3.exists(), "Missing assets/podcast_w27.mp3"
    assert w27_mp3.stat().st_size > 100000, "podcast_w27.mp3 must be a real audio file >100KB"
    assert "const audioEl = document.getElementById('nativePodcastAudio');" in html_content
    assert "audioEl.play()" in html_content