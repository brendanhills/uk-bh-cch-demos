"""Tests for presentation decoupling, JavaScript AST syntax, and data directory contracts."""

import json
from pathlib import Path
import shutil
import subprocess
import pytest


def test_javascript_ast_syntax(project_root: Path):
    """Validate that JavaScript in src/js passes syntax checks."""
    js_dir = project_root / 'src' / 'js'
    if js_dir.exists() and shutil.which('node'):
        for js_file in js_dir.rglob('*.js'):
            proc = subprocess.run(['node', '-c', str(js_file)], capture_output=True, text=True)
            assert proc.returncode == 0, f"JS Syntax error in {js_file.name}: {proc.stderr}"


def test_no_hardcoded_monolithic_datasets(project_root: Path):
    """Verify that monolithic static JSON data arrays are stripped from index.html."""
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    assert 'let LIVE_RISKS = [{"id": "RSK-001"' not in html
    assert 'let LIVE_TEAM_GOOGLE_RISKS = [{"id": "TG-RSK-001"' not in html
    assert 'let NOTEBOOK_CATALOG = {"notebookId": "acdbb29b' not in html
    assert 'const PODCAST_SCRIPTS = {' not in html
    assert 'const GEMINI_PARAGRAPHS = {' not in html


def test_dynamic_client_loader_present(project_root: Path):
    """Verify that dynamic loading functions exist in index.html or src/js modules."""
    all_content = (project_root / 'index.html').read_text(encoding='utf-8')
    js_dir = project_root / 'src' / 'js'
    if js_dir.exists():
        for js_file in js_dir.rglob('*.js'):
            all_content += js_file.read_text(encoding='utf-8')

    assert 'loadProjectData' in all_content or 'loadDashboardData' in all_content


@pytest.mark.parametrize("project", ["sample", "f-dse"])
def test_data_directories_support_client_loader(project_root: Path, project: str):
    """Verify that sample and f-dse directories contain all required files for client fetch."""
    required_files = [
        'config.json',
        'snapshots.json',
        'risks.json',
        'issues.json',
        'knowledge.json',
        'driver_tree.json'
    ]

    proj_dir = project_root / 'data' / project
    assert proj_dir.is_dir(), f"Missing data directory: {proj_dir}"
    for fname in required_files:
        fpath = proj_dir / fname
        assert fpath.is_file(), f"Missing required file for client fetch: {fpath}"
        with open(fpath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            assert data is not None
