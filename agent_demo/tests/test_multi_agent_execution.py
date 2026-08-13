"""Unit tests verifying sub-agent model compatibility and execution rules."""

import pytest
from app.cch_agent.agent import agent as router_agent
from app.cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)


def test_master_router_model_is_live_api_compatible():
    """Verify master router agent uses Live API BIDI WebSocket compatible model (gemini-live-2.5-flash-native-audio).
    
    This regression test prevents 'gemini-2.5-flash is not supported in the live api' 1007 WebSocket errors.
    """
    assert router_agent.model is not None
    assert "live" in router_agent.model.lower(), (
        f"Master router agent 'cch_concierge_router' is configured with '{router_agent.model}'. "
        f"Master router executed via runner.run_live() MUST use Live API WebSocket models (e.g. 'gemini-live-2.5-flash-native-audio')."
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
    """Verify master router agent sub-agent tools are valid AgentTool instances."""
    from google.adk.tools import AgentTool

    sub_agent_tools = [tool for tool in router_agent.tools if isinstance(tool, AgentTool)]
    assert len(sub_agent_tools) == 4
    for tool in sub_agent_tools:
        assert isinstance(tool, AgentTool)
        assert tool.agent is not None
        assert "live-" not in tool.agent.model.lower()
