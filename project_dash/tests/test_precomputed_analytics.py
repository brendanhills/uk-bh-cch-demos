import unittest
import json

from scripts.precompute_analytics import (
    compute_5x5_matrix_grid,
    compute_longitudinal_trends,
    compute_blueprint_mappings,
    compute_schedule_squeeze,
    build_precomputed_analytics
)

class TestPrecomputeAnalytics(unittest.TestCase):

    def setUp(self):
        self.sample_risks = [
            {
                'id': 'RSK-001',
                'displayId': '01',
                'status': 'Active',
                'inherentLikelihood': 4,
                'inherentConsequence': 4,
                'inherentRiskScore': 16,
                'residualLikelihood': 2,
                'residualConsequence': 3,
                'residualRiskScore': 6,
                'causeCategory': 'Engineering/Platform',
                'bundle': 'Bundle H (Infra)',
                'driverTreeRef': '1.10b'
            },
            {
                'id': 'RSK-002',
                'displayId': '02',
                'status': 'Active',
                'inherentLikelihood': 5,
                'inherentConsequence': 4,
                'inherentRiskScore': 20,
                'residualLikelihood': 4,
                'residualConsequence': 4,
                'residualRiskScore': 16,
                'causeCategory': 'Security/Compliance',
                'bundle': 'Bundle B (Security)',
                'driverTreeRef': '1.6 GFF'
            },
            {
                'id': 'RSK-003',
                'displayId': '03',
                'status': 'Closed',
                'inherentLikelihood': 3,
                'inherentConsequence': 2,
                'inherentRiskScore': 6,
                'residualLikelihood': 1,
                'residualConsequence': 1,
                'residualRiskScore': 1,
                'causeCategory': 'Security/Compliance',
                'bundle': 'Bundle B (Security)',
                'driverTreeRef': '1.6 GFF'
            }
        ]
        self.sample_issues = [
            {'id': 'ISS-001', 'status': 'Active', 'severity': 'High', 'driverTreeRef': '1.2b', 'bundle': 'Bundle E (Governance)'}
        ]
        self.sample_snapshots = {
            'w26': {
                'weekNumber': 26,
                'weekLabel': 'Week 26',
                'date': '31 Jul 2026',
                'plans': [{'ref': '1.10b', 'status': 'RED'}, {'ref': '1.14', 'status': 'RED'}]
            },
            'w27': {
                'weekNumber': 27,
                'weekLabel': 'Week 27',
                'date': '07 Aug 2026',
                'plans': [{'ref': '1.10b', 'status': 'BLUE'}, {'ref': '1.14', 'status': 'RED'}]
            }
        }
        self.sample_knowledge = {
            'blueprints': [
                {'bundle': 'Bundle B', 'title': 'System Security Plan & ATO-C Accreditation', 'driverTreeRefs': ['1.6 GFF']},
                {'bundle': 'Bundle H', 'title': 'Managed Infrastructure & GDC Hardware', 'driverTreeRefs': ['1.10b']}
            ]
        }

    def test_5x5_matrix_grid_computation(self):
        grid = compute_5x5_matrix_grid(self.sample_risks, rating_type='residual', status_filter='open')
        # Cell (L=2, C=3) has RSK-001
        self.assertIn('RSK-001', grid['cells']['2_3']['itemIds'])
        self.assertEqual(grid['cells']['2_3']['count'], 1)
        # Cell (L=4, C=4) has RSK-002
        self.assertIn('RSK-002', grid['cells']['4_4']['itemIds'])
        self.assertEqual(grid['cells']['4_4']['count'], 1)
        # Closed risk RSK-003 is excluded under status_filter='open'
        self.assertNotIn('RSK-003', grid['cells']['1_1']['itemIds'])
        self.assertEqual(grid['totalCount'], 2)

    def test_blueprint_mapping_computation(self):
        mappings = compute_blueprint_mappings(self.sample_knowledge, self.sample_risks, self.sample_issues)
        self.assertIn('Bundle B', mappings)
        self.assertEqual(mappings['Bundle B']['activeRiskCount'], 1) # RSK-002 is active in Bundle B
        self.assertIn('Bundle H', mappings)
        self.assertEqual(mappings['Bundle H']['activeRiskCount'], 1) # RSK-001 is active in Bundle H

    def test_build_full_analytics(self):
        analytics = build_precomputed_analytics(
            self.sample_risks,
            self.sample_issues,
            self.sample_snapshots,
            self.sample_knowledge
        )
        self.assertIn('matrices', analytics)
        self.assertIn('trends', analytics)
        self.assertIn('blueprintMappings', analytics)
        self.assertIn('searchTokens', analytics)

if __name__ == '__main__':
    unittest.main()
