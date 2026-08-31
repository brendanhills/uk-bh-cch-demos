"""Automated integrity verification for domain-driven frontend ES modules."""

from pathlib import Path
import pytest

EXPECTED_MODULES = [
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


@pytest.mark.parametrize("module_rel_path", EXPECTED_MODULES)
def test_expected_module_exists(project_root: Path, module_rel_path: str):
    """Verify that every domain module exists on disk."""
    module_path = project_root / 'src' / 'js' / module_rel_path
    assert module_path.exists(), f'Missing module: {module_path}'


@pytest.mark.parametrize("module_rel_path", EXPECTED_MODULES)
def test_module_uses_es6_exports(project_root: Path, module_rel_path: str):
    """Verify that domain modules export functions and classes using standard ES6 exports."""
    module_path = project_root / 'src' / 'js' / module_rel_path
    content = module_path.read_text(encoding='utf-8')
    assert 'export ' in content or module_rel_path == 'app.js', (
        f'{module_rel_path} does not contain standard ES exports'
    )


def test_app_entry_point_binds_global_interface(project_root: Path):
    """Verify app.js wires window.app and DOMContentLoaded lifecycle."""
    app_path = project_root / 'src' / 'js' / 'app.js'
    content = app_path.read_text(encoding='utf-8')
    assert 'window.app =' in content
    assert 'initApp()' in content
    assert 'switchTab' in content
