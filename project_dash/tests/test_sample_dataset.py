import unittest
import os
import json

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sample')

class TestSampleDataset(unittest.TestCase):

    def test_config_json_schema(self):
        config_path = os.path.join(SAMPLE_DATA_DIR, 'config.json')
        self.assertTrue(os.path.exists(config_path), 'config.json must exist in data/sample/')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.assertEqual(config.get('project', {}).get('slug'), 'sample')
        self.assertIn('name', config.get('project', {}))
        self.assertIn('title', config.get('project', {}))
        self.assertIn('features', config)
        
        # Verify 4 KPI pillars
        self.assertIn('kpiPillars', config)
        self.assertEqual(len(config['kpiPillars']), 4)

    def test_risks_json_schema_and_math(self):
        risks_path = os.path.join(SAMPLE_DATA_DIR, 'risks.json')
        self.assertTrue(os.path.exists(risks_path), 'risks.json must exist in data/sample/')
        with open(risks_path, 'r', encoding='utf-8') as f:
            risks = json.load(f)
        
        if isinstance(risks, dict):
            risks = risks.get('risks', [])
            
        self.assertGreaterEqual(len(risks), 25, 'Sample risks dataset must have at least 25 records')
        
        for r in risks:
            self.assertIn('id', r)
            self.assertIn('title', r)
            self.assertIn('status', r)
            
            # Verify 5x5 range
            inh_l = int(r.get('inherentLikelihood', 1))
            inh_c = int(r.get('inherentConsequence', 1))
            res_l = int(r.get('residualLikelihood', 1))
            res_c = int(r.get('residualConsequence', 1))
            
            self.assertTrue(1 <= inh_l <= 5, f'Inherent likelihood out of range for {r.get("id")}')
            self.assertTrue(1 <= inh_c <= 5, f'Inherent consequence out of range for {r.get("id")}')
            self.assertTrue(1 <= res_l <= 5, f'Residual likelihood out of range for {r.get("id")}')
            self.assertTrue(1 <= res_c <= 5, f'Residual consequence out of range for {r.get("id")}')
            
            self.assertEqual(int(r.get('inherentRiskScore')), inh_l * inh_c)
            self.assertEqual(int(r.get('residualRiskScore')), res_l * res_c)

    def test_issues_json_schema(self):
        issues_path = os.path.join(SAMPLE_DATA_DIR, 'issues.json')
        self.assertTrue(os.path.exists(issues_path), 'issues.json must exist in data/sample/')
        with open(issues_path, 'r', encoding='utf-8') as f:
            issues = json.load(f)
            
        if isinstance(issues, dict):
            issues = issues.get('issues', [])
            
        self.assertGreaterEqual(len(issues), 10, 'Sample issues dataset must have at least 10 records')
        for iss in issues:
            self.assertIn('id', iss)
            self.assertIn('title', iss)
            self.assertIn('severity', iss)
            self.assertIn('status', iss)

    def test_snapshots_json_schema(self):
        snapshots_path = os.path.join(SAMPLE_DATA_DIR, 'snapshots.json')
        self.assertTrue(os.path.exists(snapshots_path), 'snapshots.json must exist in data/sample/')
        with open(snapshots_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        snapshots = data.get('snapshots', {})
        self.assertGreaterEqual(len(snapshots), 6, 'Sample snapshots must have at least 6 historical weeks')
        
        # Verify latest snapshot structure
        latest = [s for s in snapshots.values() if s.get('isLatest') or s.get('isCurrent')]
        self.assertTrue(len(latest) >= 1)
        latest_snap = latest[0]
        self.assertIn('synthesis', latest_snap)
        self.assertIn('top3', latest_snap)
        self.assertIn('sleeperOutlier', latest_snap)
        self.assertIn('podcastScript', latest_snap)

    def test_driver_tree_and_knowledge_schema(self):
        dt_path = os.path.join(SAMPLE_DATA_DIR, 'driver_tree.json')
        self.assertTrue(os.path.exists(dt_path), 'driver_tree.json must exist in data/sample/')
        
        kb_path = os.path.join(SAMPLE_DATA_DIR, 'knowledge.json')
        self.assertTrue(os.path.exists(kb_path), 'knowledge.json must exist in data/sample/')
        with open(kb_path, 'r', encoding='utf-8') as f:
            kb = json.load(f)
        self.assertGreaterEqual(len(kb.get('blueprints', [])), 8)

if __name__ == '__main__':
    unittest.main()
