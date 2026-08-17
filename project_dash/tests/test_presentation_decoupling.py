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
        """Validate that all inline JavaScript in index.html passes syntax check."""
        import shutil
        scripts = re.findall(r'<script>(.*?)</script>', self.html_content, re.DOTALL)
        self.assertTrue(len(scripts) > 0, "No <script> tags found in index.html")
        
        combined_js = '\n'.join(scripts)
        if shutil.which('node'):
            proc = subprocess.run(
                ['node', '-c'],
                input=combined_js,
                text=True,
                capture_output=True
            )
            self.assertEqual(
                proc.returncode, 0,
                f"JavaScript syntax error in index.html: {proc.stderr}"
            )
        else:
            # Fallback basic structural verification when node runtime is not present
            self.assertIn("function initApp", combined_js)
            self.assertIn("function switchTab", combined_js)

    def test_no_hardcoded_monolithic_datasets(self):
        """Verify that monolithic static JSON data arrays are stripped from index.html."""
        # Check that LIVE_RISKS is not hardcoded with massive literal array
        self.assertNotIn('let LIVE_RISKS = [{"id": "RSK-001"', self.html_content)
        self.assertNotIn('let LIVE_TEAM_GOOGLE_RISKS = [{"id": "TG-RSK-001"', self.html_content)
        self.assertNotIn('let NOTEBOOK_CATALOG = {"notebookId": "acdbb29b', self.html_content)
        self.assertNotIn('const PODCAST_SCRIPTS = {', self.html_content)
        self.assertNotIn('const GEMINI_PARAGRAPHS = {', self.html_content)

    def test_dynamic_client_loader_present(self):
        """Verify that dynamic loading functions exist in index.html."""
        self.assertIn('async function loadDashboardData()', self.html_content)
        self.assertIn('function renderProjectBranding()', self.html_content)
        self.assertIn('function renderFeatureTabs()', self.html_content)
        self.assertIn('function getPodcastScriptForWeek(', self.html_content)
        self.assertIn('function getGeminiParagraphsForWeek(', self.html_content)

    def test_data_directories_support_client_loader(self):
        """Verify that sample and f-dse directories contain all required files for client fetch."""
        required_files = [
            'config.json',
            'snapshots.json',
            'risks.json',
            'issues.json',
            'knowledge.json',
            'driver_tree.json',
            'precomputed_analytics.json'
        ]
        
        for project in ['sample', 'f-dse']:
            proj_dir = os.path.join(self.base_dir, 'data', project)
            self.assertTrue(os.path.isdir(proj_dir), f"Missing data directory: {proj_dir}")
            for fname in required_files:
                fpath = os.path.join(proj_dir, fname)
                self.assertTrue(os.path.isfile(fpath), f"Missing required file for client fetch: {fpath}")
                # Verify JSON is valid
                with open(fpath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        self.assertIsNotNone(data)
                    except json.JSONDecodeError as e:
                        self.fail(f"Invalid JSON in {fpath}: {e}")

if __name__ == '__main__':
    unittest.main()
