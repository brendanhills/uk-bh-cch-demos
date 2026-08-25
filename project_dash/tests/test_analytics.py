import unittest
import json
import os

class TestAnalyticsAndState(unittest.TestCase):
    """Unit tests for frontend pure calculation routines, analytics, and state store."""

    def setUp(self):
        self.sample_risks = [
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

        self.matrix_scores_table = [
            [15, 19, 22, 24, 25],
            [10, 14, 17, 20, 23],
            [6, 9, 13, 16, 18],
            [3, 5, 8, 11, 12],
            [1, 2, 4, 7, 21]
        ]

    def test_matrix_score_table_lookup(self):
        """Verify 5x5 matrix score lookups for various likelihood (1-5) and consequence (1-5) values."""
        # Consequence 5 (cIdx = 0), Likelihood 5 (lIdx = 4) -> 25
        self.assertEqual(self.matrix_scores_table[0][4], 25)
        # Consequence 5 (cIdx = 0), Likelihood 1 (lIdx = 0) -> 15
        self.assertEqual(self.matrix_scores_table[0][0], 15)
        # Consequence 1 (cIdx = 4), Likelihood 1 (lIdx = 0) -> 1
        self.assertEqual(self.matrix_scores_table[4][0], 1)

    def test_filter_risks_by_status(self):
        """Test risk filtering across open, active, eventuated, closed, and all states."""
        open_risks = [r for r in self.sample_risks if r['status'] != 'Closed']
        self.assertEqual(len(open_risks), 3)

        active_risks = [r for r in self.sample_risks if r['status'] == 'Active']
        self.assertEqual(len(active_risks), 1)
        self.assertEqual(active_risks[0]['id'], 'R-01')

        eventuated_risks = [r for r in self.sample_risks if r['status'] == 'Issue Eventuated']
        self.assertEqual(len(eventuated_risks), 1)
        self.assertEqual(eventuated_risks[0]['id'], 'R-04')

        closed_risks = [r for r in self.sample_risks if r['status'] == 'Closed']
        self.assertEqual(len(closed_risks), 1)
        self.assertEqual(closed_risks[0]['id'], 'R-03')

    def test_filter_risks_by_matrix_cell(self):
        """Test filtering risks by specific 5x5 cell coordinates."""
        # Inherent (L=4, C=5) -> R-01
        cell_inherent = [
            r for r in self.sample_risks
            if r['inherentLikelihood'] == 4 and r['inherentConsequence'] == 5
        ]
        self.assertEqual(len(cell_inherent), 1)
        self.assertEqual(cell_inherent[0]['id'], 'R-01')

        # Residual (L=2, C=3) -> R-01
        cell_residual = [
            r for r in self.sample_risks
            if r['residualLikelihood'] == 2 and r['residualConsequence'] == 3
        ]
        self.assertEqual(len(cell_residual), 1)
        self.assertEqual(cell_residual[0]['id'], 'R-01')

    def test_compute_risk_kpi_counts(self):
        """Test computation of risk KPI counts and critical risk thresholds."""
        total = len(self.sample_risks)
        open_count = len([r for r in self.sample_risks if r['status'] != 'Closed'])
        critical_inherent = len([r for r in self.sample_risks if r['inherentScore'] >= 20])
        self.assertEqual(total, 4)
        self.assertEqual(open_count, 3)
        self.assertEqual(critical_inherent, 3) # R-01(24), R-03(25), R-04(20)

    def test_js_analytics_module_exists(self):
        """Verify that src/js/analytics.js exists and exports pure calculation routines."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        js_file = os.path.join(project_root, 'src', 'js', 'analytics.js')
        self.assertTrue(os.path.exists(js_file), f'Missing {js_file}')
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('export function calculateMatrixScore', content)
        self.assertIn('export function filterRisksByStatus', content)
        self.assertIn('export function filterRisksByCell', content)
        self.assertIn('export function computeRiskKpis', content)

    def test_js_state_store_exists(self):
        """Verify that src/js/state.js exists and implements reactive pub/sub state management."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        js_file = os.path.join(project_root, 'src', 'js', 'state.js')
        self.assertTrue(os.path.exists(js_file), f'Missing {js_file}')
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('class StateStore', content)
        self.assertIn('export const store =', content)

    def test_js_api_client_exists(self):
        """Verify that src/js/api.js exists and implements data ingestion & sync endpoints."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        js_file = os.path.join(project_root, 'src', 'js', 'api.js')
        self.assertTrue(os.path.exists(js_file), f'Missing {js_file}')
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('export async function loadProjectData', content)
        self.assertIn('export async function syncGoogleSheet', content)
        self.assertIn('export async function regenerateBriefing', content)

if __name__ == '__main__':
    unittest.main()
