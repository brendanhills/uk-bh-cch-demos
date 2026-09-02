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
    assert "Differentiate clearly between the caller (parent/carer) and the child patient" in ROUTER_INSTRUCTION
    assert "Always ask for and validate the caller's Australian contact phone number" in ROUTER_INSTRUCTION
    assert "Complete phone number verification BEFORE prompting the caller to upload or scan discharge paperwork" in ROUTER_INSTRUCTION


def test_bug_56_zero_assumption_child_name_rule():
    """Verify BUG-56 instructions enforcing zero assumption of child patient name."""
    assert "Zero-Assumption Rule" in ROUTER_INSTRUCTION
    assert "NEVER assume, invent, or guess the child patient's name before the caller explicitly provides it" in ROUTER_INSTRUCTION
    assert "Do NOT refer to the child by any assumed name (such as \"Leo\") unless explicitly stated" in ROUTER_INSTRUCTION


def test_router_tools():
    """Verify router agent directly attaches Python domain tools."""
    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "validate_phone_number" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "schedule_home_care_visit" in tool_names
