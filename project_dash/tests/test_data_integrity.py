import json
import unittest

class TestDataIntegrity(unittest.TestCase):
    def test_live_data_schema(self):
        with open('src/data/live_synced_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('risks', data)
        self.assertIn('teamGoogleRisks', data)
        self.assertIn('registers', data)
        self.assertIn('issues', data)
        self.assertEqual(len(data['risks']), 107)
        self.assertGreaterEqual(len(data['teamGoogleRisks']), 12)
        self.assertEqual(len(data['issues']), 29)
        
        # Verify joint risks schema
        for r in data['risks']:
            self.assertIn(r['status'], ['Active', 'Closed', 'Issue Eventuated'])
            self.assertIn(r['trend'], ['↔', '↑', '↓'])
            self.assertEqual(r.get('sourceRegister'), 'joint')
            self.assertGreaterEqual(r['inherentLikelihood'], 1)
            self.assertLessEqual(r['inherentLikelihood'], 5)
            self.assertGreaterEqual(r['inherentConsequence'], 1)
            self.assertLessEqual(r['inherentConsequence'], 5)
            self.assertTrue(len(r['riskName']) > 0)
            self.assertTrue(len(r['riskOwner']) > 0)

        # Verify Team Google risks schema
        for gr in data['teamGoogleRisks']:
            self.assertIn(gr['status'], ['Active', 'Closed', 'Issue Eventuated'])
            self.assertIn(gr['trend'], ['↔', '↑', '↓'])
            self.assertEqual(gr.get('sourceRegister'), 'teamGoogle')
            self.assertGreaterEqual(gr['inherentLikelihood'], 1)
            self.assertLessEqual(gr['inherentLikelihood'], 5)
            self.assertGreaterEqual(gr['inherentConsequence'], 1)
            self.assertLessEqual(gr['inherentConsequence'], 5)
            self.assertTrue(len(gr['riskName']) > 0)
            self.assertTrue(len(gr['riskOwner']) > 0)

    def test_index_html_canvas_binding(self):
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="chartBurndownTimeline"', html)
        self.assertIn("document.getElementById('chartBurndownTimeline')", html)
        self.assertNotIn("document.getElementById('chartBurndownBurnup')", html)

if __name__ == '__main__':
    unittest.main()
