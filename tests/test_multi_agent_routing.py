"""Unit tests verifying ADK 2.0 multi-agent router & sub-agent delegation setup."""

import pytest
from google.adk.tools import AgentTool
from app.cch_agent.agent import agent as router_agent
from app.cch_agent.sub_agents import (
    patient_verifier,
    document_scanner,
    visit_scheduler,
    soap_generator,
)


def test_master_router_agent_configuration():
    """Verify master router agent is configured with sub-agent tools."""
    assert router_agent.name == "cch_concierge_router"
    assert len(router_agent.tools) == 4
    
    tool_agent_names = [tool.agent.name for tool in router_agent.tools if isinstance(tool, AgentTool)]
    assert "patient_verifier" in tool_agent_names
    assert "document_scanner" in tool_agent_names
    assert "visit_scheduler" in tool_agent_names
    assert "soap_generator" in tool_agent_names


def test_sub_agents_instantiation():
    """Verify individual sub-agents are properly defined with their names and roles."""
    assert patient_verifier.name == "patient_verifier"
    assert "Patient Verification Specialist" in patient_verifier.instruction

    assert document_scanner.name == "document_scanner"
    assert "Clinical Document & Vision Specialist" in document_scanner.instruction

    assert visit_scheduler.name == "visit_scheduler"
    assert "Visit Scheduler" in visit_scheduler.instruction

    assert soap_generator.name == "soap_generator"
    assert "SOAP Note Specialist" in soap_generator.instruction


def test_visit_scheduler_domain_tools():
    """Verify visit_scheduler sub-agent is equipped with all 6 existing domain function tools."""
    assert len(visit_scheduler.tools) == 6
    tool_names = [getattr(tool, "__name__", str(tool)) for tool in visit_scheduler.tools]
    assert "get_home_care_cost_estimate" in tool_names
    assert "approve_funding_subsidy" in tool_names
    assert "apply_subsidy_to_support_plan" in tool_names
    assert "get_available_support_times" in tool_names
    assert "schedule_home_care_visit" in tool_names
    assert "update_hospital_emr" in tool_names
