"""Unit tests for the consolidated unified pipeline engine (scripts/pipeline.py)."""

import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from scripts.pipeline import (
    parse_report_metadata,
    compute_risk_metrics,
    generate_fallback_synthesis,
    generate_fallback_podcast,
    sync_project_data,
    ingest_report_file
)
import scripts.gemini_generator as gg


@pytest.mark.parametrize("filename, fallback_week, expected_week, expected_label, expected_date_substr", [
    ("Weekly Reporting - Week 28 - 14 Aug 2026.pdf", None, 28, "Week 28", "14 Aug 2026"),
    ("W29_Executive_Summary_21Aug2026.pdf", None, 29, None, "Aug"),
    ("Status_Report_Final.pdf", 30, 30, "Week 30", None),
])
def test_parse_report_metadata_various_formats(
    filename: str, fallback_week: int | None, expected_week: int, expected_label: str | None, expected_date_substr: str | None
):
    """Verify filename regex parsing across standard, abbreviated, and fallback naming patterns."""
    kwargs = {"use_gemini": False}
    if fallback_week is not None:
        kwargs["fallback_week"] = fallback_week

    meta = parse_report_metadata(filename, **kwargs)
    assert meta["week_number"] == expected_week
    if expected_label:
        assert meta["week_label"] == expected_label
    if expected_date_substr:
        assert expected_date_substr in meta["report_date"]


def test_compute_risk_metrics():
    """Verify mathematical computation of risk compression, counts, and averages."""
    risks = [
        {"inherentRiskScore": 20, "residualRiskScore": 6, "status": "Active"},
        {"inherentRiskScore": 15, "residualRiskScore": 9, "status": "Eventuated"},
        {"inherentRiskScore": 10, "residualRiskScore": 4, "status": "Active"}
    ]
    issues = [{"id": "ISS-01"}, {"id": "ISS-02"}]
    metrics = compute_risk_metrics(risks, issues)

    assert metrics['total_risks'] == 3
    assert metrics['total_issues'] == 2
    assert metrics['eventuated_issues_count'] == 1
    assert metrics['inherent_avg_score'] == 15.0
    assert metrics['residual_avg_score'] == 6.3
    assert metrics['delta_compression'] == "-8.7"


def test_generate_fallback_synthesis():
    """Verify deterministic baseline synthesis generation when AI is unconfigured."""
    metrics = {
        'report_week': 'Week 28',
        'report_date': '14 Aug 2026',
        'total_risks': 14,
        'inherent_avg_score': 15.4,
        'residual_avg_score': 6.2,
        'delta_compression': '-9.2',
        'total_issues': 5,
        'eventuated_issues_count': 1
    }
    synthesis = generate_fallback_synthesis(metrics)
    assert 'synthesis' in synthesis
    assert 'top3' in synthesis
    assert 'sleeperOutlier' in synthesis
    assert len(synthesis['top3']) == 3
    assert 'executive' in synthesis['synthesis']
    assert synthesis['generatedBy'] == 'deterministic_rule_engine'


def test_generate_fallback_podcast():
    """Verify fallback multi-speaker podcast script structure and role turns."""
    metrics = {'report_week': 'Week 28', 'report_date': '14 Aug 2026'}
    synthesis = generate_fallback_synthesis(metrics)
    podcast = generate_fallback_podcast(metrics, synthesis)
    assert isinstance(podcast, list)
    assert len(podcast) >= 4
    assert podcast[0]['speaker'] == 'Alex'
    assert podcast[1]['speaker'] == 'Jordan'


def test_ingest_report_file_sandbox(tmp_path: Path):
    """Verify report ingestion in an isolated directory updates snapshots.json."""
    proj_dir = tmp_path / 'sample'
    proj_dir.mkdir(parents=True, exist_ok=True)

    # Create baseline risks.json
    risks_path = proj_dir / 'risks.json'
    risks_path.write_text(
        json.dumps([{"inherentRiskScore": 16, "residualRiskScore": 8, "status": "Active"}]),
        encoding='utf-8'
    )

    # Ingest a new report
    result = ingest_report_file(
        file_name="Weekly Reporting - Week 29 - 21 Aug 2026.pdf",
        project_name="sample",
        data_root=str(tmp_path),
        force_fallback=True
    )

    assert result['success'] is True
    assert result['week'] == 29

    # Check snapshots.json was created/updated
    snap_path = proj_dir / 'snapshots.json'
    assert snap_path.exists()
    snaps = json.loads(snap_path.read_text(encoding='utf-8'))
    assert 'Week 29' in snaps
    assert snaps['Week 29']['metrics']['total_risks'] == 1


@patch('scripts.gemini_generator.inspect_report_with_gemini')
def test_parse_report_metadata_gemini_multimodal(mock_inspect: MagicMock, tmp_path: Path):
    """Verify Gemini multimodal inspection of unstructured report PDFs."""
    mock_inspect.return_value = {
        'week_number': 31,
        'week_label': 'Week 31',
        'report_date': '28 Aug 2026',
        'title': 'Monaro Executive Risk Review',
        'summary': 'Week 31 summary pack',
        'inspectedBy': 'gemini-3.5-flash'
    }

    dummy_pdf = tmp_path / "test_report.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy content")

    meta = parse_report_metadata(str(dummy_pdf), use_gemini=True)
    assert meta['week_number'] == 31
    assert meta['week_label'] == 'Week 31'
    assert meta['report_date'] == '28 Aug 2026'
    assert meta['inspectedBy'] == 'gemini-3.5-flash'
    mock_inspect.assert_called_once()


@patch('scripts.gemini_generator.inspect_report_with_gemini')
def test_parse_report_metadata_gemini_fallback_on_error(mock_inspect: MagicMock):
    """Verify fallback to regex heuristics when Gemini multimodal inspection raises an error."""
    mock_inspect.side_effect = RuntimeError("API quota exceeded")

    meta = parse_report_metadata("Weekly Reporting - Week 28 - 14 Aug 2026.pdf", use_gemini=True)
    assert meta['week_number'] == 28
    assert meta['report_date'] == "14 Aug 2026"
    assert meta['inspectedBy'] == 'regex_heuristic'
