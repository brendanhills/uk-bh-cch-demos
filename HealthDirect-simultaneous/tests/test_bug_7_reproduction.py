#!/usr/bin/env python3
"""Targeted reproduction unit test for Bug #7.

Asserts that style.css defines custom flexbox alignment offsets for original
vs. translated speech bubbles to create a visually clear dialogue flow.
"""

import os
import pytest


def test_speech_bubble_offset_styles_exist():
    """Asserts that style.css defines alignment offsets for patient-turn and nurse-turn translations."""
    css_path = os.path.abspath("demo/web/style.css")
    assert os.path.exists(css_path), f"CSS file not found at {css_path}"
    
    with open(css_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # We require specific horizontal offset alignment rules for original vs translation speech turns
    # inside style.css to support natural side-by-side dialogue flow.
    # Currently these don't exist, so this test will fail on the first run!
    
    assert ".patient-turn.translated-turn" in content, "CSS rule '.patient-turn.translated-turn' is missing"
    assert "align-self: flex-end" in content or "align-self:flex-end" in content, "flex-end alignment is missing from CSS offsets"
