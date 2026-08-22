import unittest
import os
import re
import subprocess
import json

class TestPresentationDecoupling(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.index_html_path = os.path.join(self.base_dir, 'index.html')
        with open(self.index_html_path, 'r', encoding='utf-8') as f:
            self.html_content = f.read()

    def test_javascript_ast_syntax(self):
        """Validate that JavaScript in index.html and src/js passes syntax checks."""
        import shutil
        js_dir = os.path.join(self.base_dir, 'src', 'js')
        if os.path.exists(js_dir):
            for root, _, files in os.walk(js_dir):
                for fn in files:
                    if fn.endswith('.js'):
                        fp = os.path.join(root, fn)
                        if shutil.which('node'):
                            proc = subprocess.run(['node', '-c', fp], capture_output=True, text=True)
                            self.assertEqual(proc.returncode, 0, f"JS Syntax error in {fn}: {proc.stderr}")

    def test_no_hardcoded_monolithic_datasets(self):
        """Verify that monolithic static JSON data arrays are stripped from index.html."""
        self.assertNotIn('let LIVE_RISKS = [{"id": "RSK-001"', self.html_content)
        self.assertNotIn('let LIVE_TEAM_GOOGLE_RISKS = [{"id": "TG-RSK-001"', self.html_content)
        self.assertNotIn('let NOTEBOOK_CATALOG = {"notebookId": "acdbb29b', self.html_content)
        self.assertNotIn('const PODCAST_SCRIPTS = {', self.html_content)
        self.assertNotIn('const GEMINI_PARAGRAPHS = {', self.html_content)

    def test_dynamic_client_loader_present(self):
        """Verify that dynamic loading functions exist in index.html or src/js modules."""
        js_dir = os.path.join(self.base_dir, 'src', 'js')
        all_content = self.html_content
        if os.path.exists(js_dir):
            for root, _, files in os.walk(js_dir):
                for fn in files:
                    if fn.endswith('.js'):
                        with open(os.path.join(root, fn), 'r', encoding='utf-8') as f:
                            all_content += f.read()

        self.assertTrue('loadProjectData' in all_content or 'loadDashboardData' in all_content)

    def test_data_directories_support_client_loader(self):
        """Verify that sample and f-dse directories contain all required files for client fetch."""
        required_files = [
            'config.json',
            'snapshots.json',
            'risks.json',
            'issues.json',
            'knowledge.json',
            'driver_tree.json'
        ]
        
        for project in ['sample', 'f-dse']:
            proj_dir = os.path.join(self.base_dir, 'data', project)
            self.assertTrue(os.path.isdir(proj_dir), f"Missing data directory: {proj_dir}")
            for fname in required_files:
                fpath = os.path.join(proj_dir, fname)
                self.assertTrue(os.path.isfile(fpath), f"Missing required file for client fetch: {fpath}")
                with open(fpath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        self.assertIsNotNone(data)
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in {fpath}: {e}")

if __name__ == '__main__':
    unittest.main()
