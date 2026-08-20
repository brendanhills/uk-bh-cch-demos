import unittest
import json
import os

class TestRegisterSeparation(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_config_register_names(self):
        config_path = os.path.join(self.base_dir, 'data', 'f-dse', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        project = config.get('project', {})
        self.assertEqual(project.get('primaryRegisterName'), 'Internal Risks')
        self.assertEqual(project.get('secondaryRegisterName'), 'Team Google Risks')
        self.assertEqual(project.get('title'), 'Future Defence Secret Environment')

    def test_data_counts(self):
        risks_path = os.path.join(self.base_dir, 'data', 'f-dse', 'risks.json')
        with open(risks_path, 'r', encoding='utf-8') as f:
            risks = json.load(f)
        self.assertEqual(len(risks), 119)
        internal = [r for r in risks if not (r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-'))]
        tg = [r for r in risks if r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-')]
        self.assertEqual(len(internal), 107)
        self.assertEqual(len(tg), 12)

    def test_index_html_tabs(self):
        index_path = os.path.join(self.base_dir, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        self.assertIn('id="tab-overview"', html)
        self.assertIn('id="tab-team-google"', html)
        self.assertIn('id="tabPrimaryRegisterLabel"', html)
        self.assertIn('id="tabSecondaryRegisterLabel"', html)
        self.assertIn('Internal Risks', html)
        self.assertIn('Team Google Risks', html)
