import os
import sys
import json
import pytest
import tempfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.pipeline import (
    parse_report_metadata,
    compute_risk_metrics,
    generate_fallback_synthesis,
    generate_fallback_podcast,
    sync_project_data,
    ingest_report_file
)

def test_parse_report_metadata_various_formats():
    # Standard format
    meta1 = parse_report_metadata("Weekly Reporting - Week 28 - 14 Aug 2026.pdf")
    assert meta1['week_number'] == 28
    assert meta1['report_date'] == "14 Aug 2026"
    assert meta1['week_label'] == "Week 28"

    # W29 abbreviation format
    meta2 = parse_report_metadata("W29_Executive_Summary_21Aug2026.pdf")
    assert meta2['week_number'] == 29
    assert "Aug" in meta2['report_date']

    # Non-standard name with fallback
    meta3 = parse_report_metadata("Status_Report_Final.pdf", fallback_week=30)
    assert meta3['week_number'] == 30
    assert meta3['week_label'] == "Week 30"

def test_compute_risk_metrics():
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
    metrics = {'report_week': 'Week 28', 'report_date': '14 Aug 2026'}
    synthesis = generate_fallback_synthesis(metrics)
    podcast = generate_fallback_podcast(metrics, synthesis)
    assert isinstance(podcast, list)
    assert len(podcast) >= 4
    assert podcast[0]['speaker'] == 'Alex'
    assert podcast[1]['speaker'] == 'Jordan'

def test_ingest_report_file_sandbox():
    with tempfile.TemporaryDirectory() as tmp_dir:
        proj_dir = os.path.join(tmp_dir, 'sample')
        os.makedirs(proj_dir, exist_ok=True)
        
        # Create baseline risks.json
        risks_path = os.path.join(proj_dir, 'risks.json')
        with open(risks_path, 'w') as f:
            json.dump([{"inherentRiskScore": 16, "residualRiskScore": 8, "status": "Active"}], f)

        # Ingest a new report
        result = ingest_report_file(
            file_name="Weekly Reporting - Week 29 - 21 Aug 2026.pdf",
            project_name="sample",
            data_root=tmp_dir,
            force_fallback=True
        )

        assert result['success'] is True
        assert result['week'] == 29

        # Check snapshots.json was created/updated
        snap_path = os.path.join(proj_dir, 'snapshots.json')
        assert os.path.exists(snap_path)
        with open(snap_path, 'r') as f:
            snaps = json.load(f)
        assert 'Week 29' in snaps
        assert snaps['Week 29']['metrics']['total_risks'] == 1
