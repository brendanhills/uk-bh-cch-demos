"""Tests verifying strict register separation between Joint Program and Team Google risks."""

import json
from pathlib import Path
import pytest


def test_config_register_names(project_root: Path):
    """Verify primary and secondary register names in project configuration."""
    config_path = project_root / 'data' / 'f-dse' / 'config.json'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    project = config.get('project', {})
    assert project.get('primaryRegisterName') == 'Internal Risks'
    assert project.get('secondaryRegisterName') == 'Team Google Risks'
    assert project.get('title') == 'Monaro'


def test_data_counts(project_root: Path):
    """Verify total, internal, and Team Google risk counts in f-dse risks.json."""
    risks_path = project_root / 'data' / 'f-dse' / 'risks.json'
    with open(risks_path, 'r', encoding='utf-8') as f:
        risks = json.load(f)
    assert len(risks) == 119
    internal = [
        r for r in risks
        if not (r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-'))
    ]
    tg = [
        r for r in risks
        if r.get('sourceRegister') == 'team_google' or str(r.get('id')).startswith('TG-') or str(r.get('id')).startswith('AUR-TG-')
    ]
    assert len(internal) == 107
    assert len(tg) == 12


def test_index_html_tabs(project_root: Path):
    """Verify tab labels and containers for both registers exist in index.html."""
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    assert 'id="tab-overview"' in html
    assert 'id="tab-team-google"' in html
    assert 'id="tabPrimaryRegisterLabel"' in html
    assert 'id="tabSecondaryRegisterLabel"' in html
    assert 'Internal Risks' in html
    assert 'Team Google Risks' in html
