#!/usr/bin/env python3
"""Targeted reproduction unit test for Bug #8.

Asserts that simultaneous_client.js correctly clears speech bubble tracking anchors
multiple times (specifically inside both turn completion and transcript finalization).
"""

import os
import pytest


def test_bubble_anchor_cleared_on_final():
    """Asserts that client-side JS clears bubble anchors inside the isFinal check block as well as completeTurn."""
    js_path = os.path.abspath("demo/web/simultaneous_client.js")
    assert os.path.exists(js_path), f"JS file not found at {js_path}"
    
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # We expect that when isFinal is true, the tracking variables are set to null.
    # Therefore, they must be cleared at least TWICE in the codebase (once in completeTurn and once in updateSpeechText).
    pat_count = content.count("currentPatientOriginalBubble = null") + content.count("currentPatientOriginalBubble=null")
    nurse_count = content.count("currentNurseOriginalBubble = null") + content.count("currentNurseOriginalBubble=null")
    
    assert pat_count >= 2, f"currentPatientOriginalBubble is only cleared {pat_count} time(s). Must be cleared when final too."
    assert nurse_count >= 2, f"currentNurseOriginalBubble is only cleared {nurse_count} time(s). Must be cleared when final too."
