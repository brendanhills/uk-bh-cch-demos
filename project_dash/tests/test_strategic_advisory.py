"""Tests verifying strategic advisory elements, classification banners, and governance badges."""

from pathlib import Path
import pytest


def test_google_need_to_know_global_banner(project_root: Path):
    """Verify Google Need to Know (NTK) classification badge is in the title banner."""
    html = (project_root / 'index.html').read_text(encoding='utf-8')
    assert 'id="ntkClassificationBadge"' in html
    assert 'Google Need to Know (NTK)' in html
