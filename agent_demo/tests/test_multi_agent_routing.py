"""Unit tests verifying ADK 2.0 concierge router configuration and tool attachments."""

import pytest
from app.cch_agent.agent import agent as router_agent


def test_master_router_agent_configuration():
    """Verify master router agent is configured with direct domain tools."""
    assert router_agent.name == "cch_concierge_router"
    assert len(router_agent.tools) == 7
    
    tool_names = [getattr(t, "__name__", str(t)) for t in router_agent.tools]
    assert "validate_phone_number" in tool_names
    assert "record_patient_identity" in tool_names
    assert "calculate_home_care_financials" in tool_names
    assert "approve_funding_subsidy" in tool_names
    assert "get_available_support_times" in tool_names
    assert "schedule_home_care_visit" in tool_names
    assert "update_hospital_emr" in tool_names
