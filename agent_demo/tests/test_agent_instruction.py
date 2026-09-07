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
    assert "CONSULTATION WRAP-UP & CLINICAL SOAP EXPORT" in ROUTER_INSTRUCTION


def test_bug_55_parent_child_disambiguation_and_phone_verification():
    """Verify BUG-55 instructions for parent/child name disambiguation and mandatory phone verification."""
    assert "Name & Role Disambiguation" in ROUTER_INSTRUCTION
    assert "Differentiate clearly between the caller (parent/carer) and the child patient" in ROUTER_INSTRUCTION
    assert "Always ask for and validate the caller's Australian contact phone number" in ROUTER_INSTRUCTION
    assert "Complete phone number verification BEFORE prompting the caller to upload or scan discharge paperwork" in ROUTER_INSTRUCTION


def test_bug_56_zero_assumption_child_name_rule():
    """Verify BUG-56 positive behavioral instructions for child patient name handling."""
    assert "Patient Name Protocol" in ROUTER_INSTRUCTION
    assert "Refer to the child patient strictly and exclusively by the exact name provided verbally by the caller or read from an attached discharge document" in ROUTER_INSTRUCTION
    assert "If the caller has not mentioned their child's name yet, politely ask for the child's name or wait until inspecting the discharge paperwork" in ROUTER_INSTRUCTION


def test_router_tools():
    """Verify router agent directly attaches Python domain tools."""
    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "validate_phone_number" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "schedule_home_care_visit" in tool_names
    assert "complete_consultation_and_export_soap" in tool_names
