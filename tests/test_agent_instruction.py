"""Unit tests verifying agent router instructions and direct pipeline tools."""

import pytest
from app.cch_agent.agent import ROUTER_INSTRUCTION, agent


def test_router_instruction():
    """Verify master concierge router instruction defines global rules and topic sections."""
    assert "Jennie" in ROUTER_INSTRUCTION
    assert "GLOBAL MULTILINGUAL PROTOCOL" in ROUTER_INSTRUCTION
    assert "GREETING & IDENTITY VERIFICATION" in ROUTER_INSTRUCTION
    assert "DISCHARGE PAPERWORK & MULTIMODAL VISION" in ROUTER_INSTRUCTION
    assert "FUNDING SUBSIDIES & NURSE VISIT BOOKING" in ROUTER_INSTRUCTION


def test_bug_55_parent_child_disambiguation_and_phone_verification():
    """Verify BUG-55 instructions for parent/child name disambiguation and mandatory phone verification."""
    assert "Name & Role Disambiguation" in ROUTER_INSTRUCTION
    assert "Differentiate clearly between the caller (parent/carer, e.g., Brendan) and the child patient (e.g., Leo)" in ROUTER_INSTRUCTION
    assert "NEVER address the caller by the child's name" in ROUTER_INSTRUCTION
    assert "Always ask for and validate the caller's Australian contact phone number" in ROUTER_INSTRUCTION
    assert "Complete phone number verification BEFORE prompting the caller to upload or scan discharge paperwork" in ROUTER_INSTRUCTION


def test_router_tools():
    """Verify router agent directly attaches Python domain tools."""
    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "validate_phone_number" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "schedule_home_care_visit" in tool_names
