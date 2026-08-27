import unittest
import os
import json
import shutil
import tempfile
from unittest.mock import patch, MagicMock

from scripts.pipeline import (
    resolve_target_projects,
    load_project_config,
    ingest_single_project
)

class TestIngestData(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sample_proj_dir = os.path.join(self.test_dir, 'data', 'sample')
        os.makedirs(self.sample_proj_dir, exist_ok=True)
        
        self.sample_config = {
            'project': {
                'slug': 'sample',
                'name': 'Project Aurora',
                'title': 'Enterprise AI Transformation',
                'organization': 'Acme Corp'
            },
            'sources': {
                'googleSheets': {
                    'enabled': False,
                    'sheetUrl': ''
                },
                'googleDrive': {
                    'enabled': False,
                    'folderId': ''
                },
                'geminiNotebooks': {
                    'enabled': False,
                    'notebookIds': []
                }
            },
            'features': {
                'secondaryRegister': {'enabled': True},
                'audioBriefing': {'enabled': True}
            }
        }
        with open(os.path.join(self.sample_proj_dir, 'config.json'), 'w') as f:
            json.dump(self.sample_config, f)

        # Write dummy data files
        with open(os.path.join(self.sample_proj_dir, 'risks.json'), 'w') as f:
            json.dump([{'id': 'RSK-001', 'inherentRiskScore': 16, 'residualRiskScore': 6, 'status': 'Active'}], f)
        with open(os.path.join(self.sample_proj_dir, 'issues.json'), 'w') as f:
            json.dump([], f)
        with open(os.path.join(self.sample_proj_dir, 'snapshots.json'), 'w') as f:
            json.dump({'snapshots': {'w1': {'weekNumber': 1, 'weekLabel': 'Week 1', 'date': '01 Aug 2026'}}}, f)
        with open(os.path.join(self.sample_proj_dir, 'knowledge.json'), 'w') as f:
            json.dump({'blueprints': []}, f)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_resolve_target_projects_explicit_cli(self):
        projects = resolve_target_projects(cli_arg='f-dse')
        self.assertEqual(projects, ['f-dse'])

    def test_resolve_target_projects_env_list(self):
        with patch.dict(os.environ, {'DEFAULT_PROJECTS': 'f-dse, sample, custom-app'}):
            projects = resolve_target_projects(cli_arg=None)
            self.assertEqual(projects, ['f-dse', 'sample', 'custom-app'])

    def test_resolve_target_projects_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            projects = resolve_target_projects(cli_arg=None)
            self.assertEqual(projects, ['sample'])

    def test_load_project_config(self):
        with patch('scripts.pipeline.DATA_BASE_DIR', os.path.join(self.test_dir, 'data')):
            config = load_project_config('sample')
            self.assertEqual(config['project']['name'], 'Project Aurora')

    def test_ingest_single_project_pipeline(self):
        with patch('scripts.pipeline.DATA_BASE_DIR', os.path.join(self.test_dir, 'data')):
            result = ingest_single_project('sample', generate_ai=False)
            self.assertTrue(result['success'])
            self.assertEqual(result['totalRisks'], 1)
            self.assertEqual(result['totalIssues'], 0)

if __name__ == '__main__':
    unittest.main()
