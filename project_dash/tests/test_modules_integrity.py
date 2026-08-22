import unittest
import os
import re

class TestModularFrontendIntegrity(unittest.TestCase):
    """Automated integrity verification for domain-driven frontend ES modules."""

    def setUp(self):
        self.js_root = '/usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash/src/js'
        self.expected_modules = [
            'analytics.js',
            'state.js',
            'api.js',
            'charts.js',
            'app.js',
            'modules/exec_briefing.js',
            'modules/risk_heatmap.js',
            'modules/risk_explorer.js',
            'modules/issue_register.js',
            'modules/performance_trends.js',
            'modules/blueprint_knowledge.js',
            'modules/driver_tree.js',
            'modules/time_machine.js',
            'modules/modals.js'
        ]

    def test_all_expected_modules_exist(self):
        """Verify that every domain module exists on disk."""
        for mod in self.expected_modules:
            p = os.path.join(self.js_root, mod)
            self.assertTrue(os.path.exists(p), f'Missing module: {p}')

    def test_modules_use_es6_exports(self):
        """Verify that domain modules export functions and classes using standard ES6 exports."""
        for mod in self.expected_modules:
            p = os.path.join(self.js_root, mod)
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertTrue(
                'export ' in content or mod == 'app.js',
                f'{mod} does not contain standard ES exports'
            )

    def test_app_entry_point_binds_global_interface(self):
        """Verify app.js wires window.app and DOMContentLoaded lifecycle."""
        app_path = os.path.join(self.js_root, 'app.js')
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('window.app =', content)
        self.assertIn('initApp()', content)
        self.assertIn('switchTab', content)

if __name__ == '__main__':
    unittest.main()
