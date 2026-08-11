import json
import unittest

class TestDataIntegrity(unittest.TestCase):
    def test_live_data_schema(self):
        with open('src/data/live_synced_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('risks', data)
        self.assertIn('issues', data)
        self.assertEqual(len(data['risks']), 107)
        self.assertEqual(len(data['issues']), 29)
        
        # Verify columns are aligned and not shifted
        for r in data['risks']:
            self.assertIn(r['status'], ['Active', 'Closed', 'Issue Eventuated'])
            self.assertIn(r['trend'], ['↔', '↑', '↓'])
            self.assertGreaterEqual(r['inherentLikelihood'], 1)
            self.assertLessEqual(r['inherentLikelihood'], 5)
            self.assertGreaterEqual(r['inherentConsequence'], 1)
            self.assertLessEqual(r['inherentConsequence'], 5)
            self.assertTrue(len(r['riskName']) > 0)
            self.assertTrue(len(r['riskOwner']) > 0)

    def test_index_html_canvas_binding(self):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="chartBurndownTimeline"', html)
        self.assertIn("document.getElementById('chartBurndownTimeline')", html)
        self.assertNotIn("document.getElementById('chartBurndownBurnup')", html)

if __name__ == '__main__':
    unittest.main()
