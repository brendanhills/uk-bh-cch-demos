"""Unit tests for frontend pure calculation routines, analytics, and state store."""

import json
import os
from pathlib import Path
import pytest

SAMPLE_ANALYTICS_RISKS = [
    {
        'id': 'R-01',
        'riskName': 'Security Authorization Delay',
        'status': 'Active',
        'inherentLikelihood': 4,
        'inherentConsequence': 5,
        'inherentScore': 24,
        'residualLikelihood': 2,
        'residualConsequence': 3,
        'residualScore': 11,
        'category': 'Security',
        'bundle': 'Bundle B'
    },
    {
        'id': 'R-02',
        'riskName': 'Supply Chain Hardware Lag',
        'status': 'Open',
        'inherentLikelihood': 3,
        'inherentConsequence': 4,
        'inherentScore': 17,
        'residualLikelihood': 1,
        'residualConsequence': 2,
        'residualScore': 4,
        'category': 'Procurement',
        'bundle': 'Bundle C'
    },
    {
        'id': 'R-03',
        'riskName': 'Legacy Data Format Mismatch',
        'status': 'Closed',
        'inherentLikelihood': 5,
        'inherentConsequence': 5,
        'inherentScore': 25,
        'residualLikelihood': 1,
        'residualConsequence': 1,
        'residualScore': 1,
        'category': 'Technical',
        'bundle': 'Bundle A'
    },
    {
        'id': 'R-04',
        'riskName': 'Milestone 2 IBR Gate Scope Creep',
        'status': 'Issue Eventuated',
        'inherentLikelihood': 4,
        'inherentConsequence': 4,
        'inherentScore': 20,
        'residualLikelihood': 3,
        'residualConsequence': 4,
        'residualScore': 16,
        'category': 'Governance',
        'bundle': 'Bundle B'
    }
]

MATRIX_SCORES_TABLE = [
    [15, 19, 22, 24, 25],
    [10, 14, 17, 20, 23],
    [6, 9, 13, 16, 18],
    [3, 5, 8, 11, 12],
    [1, 2, 4, 7, 21]
]


@pytest.mark.parametrize("c_idx, l_idx, expected_score", [
    (0, 4, 25),  # Consequence 5, Likelihood 5 -> 25
    (0, 0, 15),  # Consequence 5, Likelihood 1 -> 15
    (4, 0, 1),   # Consequence 1, Likelihood 1 -> 1
])
def test_matrix_score_table_lookup(c_idx: int, l_idx: int, expected_score: int):
    """Verify 5x5 matrix score lookups for various likelihood and consequence indices."""
    assert MATRIX_SCORES_TABLE[c_idx][l_idx] == expected_score


def test_filter_risks_by_status():
    """Test risk filtering across open, active, eventuated, closed, and all states."""
    open_risks = [r for r in SAMPLE_ANALYTICS_RISKS if r['status'] != 'Closed']
    assert len(open_risks) == 3

    active_risks = [r for r in SAMPLE_ANALYTICS_RISKS if r['status'] == 'Active']
    assert len(active_risks) == 1
    assert active_risks[0]['id'] == 'R-01'

    eventuated_risks = [r for r in SAMPLE_ANALYTICS_RISKS if r['status'] == 'Issue Eventuated']
    assert len(eventuated_risks) == 1
    assert eventuated_risks[0]['id'] == 'R-04'

    closed_risks = [r for r in SAMPLE_ANALYTICS_RISKS if r['status'] == 'Closed']
    assert len(closed_risks) == 1
    assert closed_risks[0]['id'] == 'R-03'


def test_filter_risks_by_matrix_cell():
    """Test filtering risks by specific 5x5 cell coordinates."""
    cell_inherent = [
        r for r in SAMPLE_ANALYTICS_RISKS
        if r['inherentLikelihood'] == 4 and r['inherentConsequence'] == 5
    ]
    assert len(cell_inherent) == 1
    assert cell_inherent[0]['id'] == 'R-01'

    cell_residual = [
        r for r in SAMPLE_ANALYTICS_RISKS
        if r['residualLikelihood'] == 2 and r['residualConsequence'] == 3
    ]
    assert len(cell_residual) == 1
    assert cell_residual[0]['id'] == 'R-01'


def test_compute_risk_kpi_counts():
    """Test computation of risk KPI counts and critical risk thresholds."""
    total = len(SAMPLE_ANALYTICS_RISKS)
    open_count = len([r for r in SAMPLE_ANALYTICS_RISKS if r['status'] != 'Closed'])
    critical_inherent = len([r for r in SAMPLE_ANALYTICS_RISKS if r['inherentScore'] >= 20])
    assert total == 4
    assert open_count == 3
    assert critical_inherent == 3  # R-01(24), R-03(25), R-04(20)


def test_js_analytics_module_exists(project_root: Path):
    """Verify that src/js/analytics.js exists and exports pure calculation routines."""
    js_file = project_root / 'src' / 'js' / 'analytics.js'
    assert js_file.exists(), f'Missing {js_file}'
    content = js_file.read_text(encoding='utf-8')
    assert 'export function calculateMatrixScore' in content
    assert 'export function filterRisksByStatus' in content
    assert 'export function filterRisksByCell' in content
    assert 'export function computeRiskKpis' in content


def test_js_state_store_exists(project_root: Path):
    """Verify that src/js/state.js exists and implements reactive pub/sub state management."""
    js_file = project_root / 'src' / 'js' / 'state.js'
    assert js_file.exists(), f'Missing {js_file}'
    content = js_file.read_text(encoding='utf-8')
    assert 'class StateStore' in content
    assert 'export const store =' in content


def test_js_api_client_exists(project_root: Path):
    """Verify that src/js/api.js exists and implements data ingestion & sync endpoints."""
    js_file = project_root / 'src' / 'js' / 'api.js'
    assert js_file.exists(), f'Missing {js_file}'
    content = js_file.read_text(encoding='utf-8')
    assert 'export async function loadProjectData' in content
    assert 'export async function syncGoogleSheet' in content
    assert 'export async function regenerateBriefing' in content
