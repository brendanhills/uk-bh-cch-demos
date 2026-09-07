"""Unit tests verifying router model compatibility and direct tool attachments."""

import pytest
from app.cch_agent.agent import agent as router_agent


def test_master_router_model_is_live_api_compatible():
    """Verify master router agent uses Live API BIDI WebSocket compatible model (gemini-live-2.5-flash-native-audio)."""
    assert router_agent.model is not None
    assert "live" in router_agent.model.lower(), (
        f"Master router agent 'cch_concierge_router' is configured with '{router_agent.model}'. "
        f"Master router executed via runner.run_live() MUST use Live API WebSocket models."
    )


def test_router_agent_direct_tools_attachment():
    """Verify master router agent tools are direct Python function tools."""
    assert len(router_agent.tools) == 8
    tool_names = [getattr(t, "__name__", str(t)) for t in router_agent.tools]
    assert "validate_phone_number" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "schedule_home_care_visit" in tool_names
    assert "complete_consultation_and_export_soap" in tool_names
