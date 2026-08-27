import os
import json
import unittest

def load_full_html():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base_dir, 'index.html'), 'r', encoding='utf-8') as f:
        html = f.read()
    js_dir = os.path.join(base_dir, 'src', 'js')
    if os.path.exists(js_dir):
        for root, _, files in os.walk(js_dir):
            for fn in sorted(files):
                if fn.endswith('.js'):
                    with open(os.path.join(root, fn), 'r', encoding='utf-8') as f:
                        html += chr(10) + f.read()
    return html


class TestDataIntegrity(unittest.TestCase):
    def test_live_data_schema(self):
        with open('data/sheets/live_synced_data.json', 'r', encoding='utf-8') as f:
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
        html = load_full_html()
        self.assertIn('id="chartBurndownTimeline"', html)
        self.assertIn("document.getElementById('chartBurndownTimeline')", html)
        self.assertNotIn("document.getElementById('chartBurndownBurnup')", html)

if __name__ == '__main__':
    unittest.main()