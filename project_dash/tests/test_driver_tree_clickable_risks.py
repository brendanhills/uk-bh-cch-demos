"""Tests verifying Driver Tree deliverable cards and risk/issue modal transitions."""

from pathlib import Path
import pytest


def load_full_html(project_root: Path) -> str:
    """Loads index.html concatenated with all ES modules under src/js/."""
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    js_dir = project_root / 'src' / 'js'
    if js_dir.exists():
        for fn in sorted(js_dir.rglob('*.js')):
            html += '\n' + fn.read_text(encoding='utf-8')
    return html


def test_render_driver_tree_has_direct_risk_modal_calls(project_root: Path):
    """Verify Driver Tree delivers direct risk and issue modal opening."""
    html = load_full_html(project_root)
    assert 'openRiskModal' in html, 'index.html must define and call openRiskModal'
    assert 'openItemDetailModal' in html, 'index.html must define openItemDetailModal'
    assert 'openRiskModal(' in html
    assert 'filterByDriverTreeDeliverable' in html


def test_filter_by_driver_tree_deliverable_function(project_root: Path):
    """Verify filterByDriverTreeDeliverable handles both risks and issues tab transitions."""
    html = load_full_html(project_root)
    assert 'function filterByDriverTreeDeliverable' in html
    assert "switchTab('overview')" in html
    assert "switchTab('issues')" in html