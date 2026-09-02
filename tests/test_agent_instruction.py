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


def test_router_tools():
    """Verify router agent directly attaches Python domain tools."""
    tool_names = [getattr(t, "__name__", str(t)) for t in agent.tools]
    assert "validate_phone_number" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "schedule_home_care_visit" in tool_names
