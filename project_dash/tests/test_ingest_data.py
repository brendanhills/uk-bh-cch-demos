"""Unit tests for data ingestion orchestration (scripts/ingest_data.py)."""

import json
from pathlib import Path
from unittest.mock import patch
import pytest

from scripts.pipeline import (
    resolve_target_projects,
    load_project_config,
    ingest_single_project
)


@pytest.fixture
def isolated_sample_env(tmp_path: Path) -> Path:
    """Sets up an isolated project environment under tmp_path/data/sample."""
    data_dir = tmp_path / 'data'
    sample_dir = data_dir / 'sample'
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_config = {
        'project': {
            'slug': 'sample',
            'name': 'Project Aurora',
            'title': 'Enterprise AI Transformation',
            'organization': 'Acme Corp'
        },
        'sources': {
            'googleSheets': {'enabled': False, 'sheetUrl': ''},
            'googleDrive': {'enabled': False, 'folderId': ''},
            'geminiNotebooks': {'enabled': False, 'notebookIds': []}
        },
        'features': {
            'secondaryRegister': {'enabled': True},
            'audioBriefing': {'enabled': True}
        }
    }
    (sample_dir / 'config.json').write_text(json.dumps(sample_config), encoding='utf-8')
    (sample_dir / 'risks.json').write_text(
        json.dumps([{'id': 'RSK-001', 'inherentRiskScore': 16, 'residualRiskScore': 6, 'status': 'Active'}]),
        encoding='utf-8'
    )
    (sample_dir / 'issues.json').write_text(json.dumps([]), encoding='utf-8')
    (sample_dir / 'snapshots.json').write_text(
        json.dumps({'snapshots': {'w1': {'weekNumber': 1, 'weekLabel': 'Week 1', 'date': '01 Aug 2026'}}}),
        encoding='utf-8'
    )
    (sample_dir / 'knowledge.json').write_text(json.dumps({'blueprints': []}), encoding='utf-8')
    return data_dir


def test_resolve_target_projects_explicit_cli():
    """Verify target project resolution when passed via explicit CLI flag."""
    projects = resolve_target_projects(cli_arg='f-dse')
    assert projects == ['f-dse']


def test_resolve_target_projects_env_list(monkeypatch: pytest.MonkeyPatch):
    """Verify target projects parsed from DEFAULT_PROJECTS comma-separated environment variable."""
    monkeypatch.setenv('DEFAULT_PROJECTS', 'f-dse, sample, custom-app')
    projects = resolve_target_projects(cli_arg=None)
    assert projects == ['f-dse', 'sample', 'custom-app']


def test_resolve_target_projects_fallback(monkeypatch: pytest.MonkeyPatch):
    """Verify fallback to ['sample'] when no project arg or environment variable is set."""
    monkeypatch.delenv('DEFAULT_PROJECTS', raising=False)
    projects = resolve_target_projects(cli_arg=None)
    assert projects == ['sample']


def test_load_project_config(isolated_sample_env: Path):
    """Verify loading configuration for a target project from the data root."""
    with patch('scripts.pipeline.DATA_BASE_DIR', str(isolated_sample_env)):
        config = load_project_config('sample')
        assert config['project']['name'] == 'Project Aurora'


def test_ingest_single_project_pipeline(isolated_sample_env: Path):
    """Verify end-to-end ingestion pipeline execution for a single project without AI generation."""
    with patch('scripts.pipeline.DATA_BASE_DIR', str(isolated_sample_env)):
        result = ingest_single_project('sample', generate_ai=False)
        assert result['success'] is True
        assert result['totalRisks'] == 1
        assert result['totalIssues'] == 0
