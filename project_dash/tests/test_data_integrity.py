"""Data integrity tests for synced risk registers and index.html bindings."""

import json
from pathlib import Path
import pytest


def load_full_html(project_root: Path) -> str:
    """Loads index.html concatenated with all ES modules under src/js/."""
    html_file = project_root / "index.html"
    html = html_file.read_text(encoding="utf-8")
    js_dir = project_root / "src" / "js"
    if js_dir.exists():
        for js_path in sorted(js_dir.rglob("*.js")):
            html += "\n" + js_path.read_text(encoding="utf-8")
    return html


def test_live_data_schema(project_root: Path):
    """Verify schema and validity constraints of data/sheets/live_synced_data.json."""
    data_file = project_root / "data" / "sheets" / "live_synced_data.json"
    assert data_file.exists(), f"Missing {data_file}"
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "risks" in data
    assert "teamGoogleRisks" in data
    assert "registers" in data
    assert "issues" in data
    assert len(data["risks"]) == 107
    assert len(data["teamGoogleRisks"]) >= 12
    assert len(data["issues"]) == 29

    # Verify joint risks schema
    for r in data["risks"]:
        assert r["status"] in ["Active", "Closed", "Issue Eventuated"]
        assert r["trend"] in ["↔", "↑", "↓"]
        assert r.get("sourceRegister") == "joint"
        assert 1 <= r["inherentLikelihood"] <= 5
        assert 1 <= r["inherentConsequence"] <= 5
        assert len(r["riskName"]) > 0
        assert len(r["riskOwner"]) > 0

    # Verify Team Google risks schema
    for gr in data["teamGoogleRisks"]:
        assert gr["status"] in ["Active", "Closed", "Issue Eventuated"]
        assert gr["trend"] in ["↔", "↑", "↓"]
        assert gr.get("sourceRegister") == "teamGoogle"
        assert 1 <= gr["inherentLikelihood"] <= 5
        assert 1 <= gr["inherentConsequence"] <= 5
        assert len(gr["riskName"]) > 0
        assert len(gr["riskOwner"]) > 0


def test_index_html_canvas_binding(project_root: Path):
    """Verify Chart.js canvas element and script binding IDs are harmonized."""
    html = load_full_html(project_root)
    assert 'id="chartBurndownTimeline"' in html
    assert "document.getElementById('chartBurndownTimeline')" in html
    assert "document.getElementById('chartBurndownBurnup')" not in html