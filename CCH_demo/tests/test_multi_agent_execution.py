"""Unit tests verifying sub-agent model compatibility and execution rules."""

import pytest
from app.cch_agent.agent import agent as router_agent
from app.cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)


def test_sub_agent_models_are_unary_api_compatible():
    """Verify sub-agents use unary generateContent API compatible models (e.g., gemini-2.5-flash) and NOT WebSocket-only live models (gemini-live-2.5-flash-native-audio).
    
    This regression test prevents INVALID_ARGUMENT 400 errors during AgentTool execution.
    """
    sub_agents = [patient_verifier, document_scanner, visit_scheduler, soap_generator]
    for sub in sub_agents:
        assert sub.model is not None, f"Sub-agent {sub.name} must have a model defined"
        assert "live-" not in sub.model.lower(), (
            f"Sub-agent '{sub.name}' is configured with WebSocket-only model '{sub.model}'. "
            f"Sub-agents called via AgentTool MUST use standard unary generateContent models (e.g., 'gemini-2.5-flash')."
        )


def test_router_agent_tools_wrapping():
    """Verify master router agent tools are valid AgentTool instances."""
    from google.adk.tools import AgentTool

    assert len(router_agent.tools) == 4
    for tool in router_agent.tools:
        assert isinstance(tool, AgentTool)
        assert tool.agent is not None
        assert "live-" not in tool.agent.model.lower()
