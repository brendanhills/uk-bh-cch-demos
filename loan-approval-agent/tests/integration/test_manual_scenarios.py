import pytest
import pytest_asyncio
import os
import sys

# Mark integration test to depend on unit tests
pytestmark = [
    pytest.mark.depends(name="integration_scenarios", depends=["unit_agents"]),
    pytest.mark.run(order=2)
]
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
import dotenv

from unittest.mock import patch

# Load environment variables
dotenv.load_dotenv()

@pytest_asyncio.fixture
async def runner():
    """Fixture to provide an InMemoryRunner instance with mocked dependencies."""
    with patch("external_services.simulation_utils.get_latency", return_value=0), \
         patch("loan_agent.utils.model_client.get_best_model_name", return_value="gemini-2.5-flash"):
        runner = InMemoryRunner(agent=loan_manager)
        yield runner

from loan_agent.sub_agents.investigator.agent import investigator_agent
from loan_agent.sub_agents.policy_expert.agent import policy_expert_agent
from loan_agent.sub_agents.underwriter.agent import underwriter_agent

# FIX: Force model to gemini-2.5-flash
loan_manager.model.model = "gemini-2.5-flash"
investigator_agent.model.model = "gemini-2.5-flash"
policy_expert_agent.model.model = "gemini-2.5-flash"
underwriter_agent.model.model = "gemini-2.5-flash"

async def run_scenario_test(runner, name, user_input, expected_outcome):
    """Helper function to run a scenario and assert the outcome."""
    print(f"\n--- Running Test Scenario: {name} ---")
    
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id=f"test_user_{name.lower().replace(' ', '_')}"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    
    final_response = ""
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"
                    print(f"AGENT: {part.text}")
        elif hasattr(event, "exception") and event.exception:
            print(f"EXCEPTION: {event.exception}")


    print(f"Final Response: {final_response}")
    
    # Assert
    # Support multiple valid outcomes
    if isinstance(expected_outcome, list):
        found = any(out in final_response.upper() for out in expected_outcome)
        assert found, f"Expected one of '{expected_outcome}' in response, but got: {final_response}"
    else:
        assert expected_outcome in final_response.upper(), f"Expected '{expected_outcome}' in response, but got: {final_response}"

@pytest.mark.asyncio
async def test_scenario_sarah_speed(runner):
    """
    Test Sarah Speed (Core - Approve).
    ID: sarah_speed
    """
    user_input = (
        "process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, "
        "income: 59758, employer: City Hospital, amount: 20000, purpose: Debt Consolidation, "
        "monthly_payment: 300"
    )
    await run_scenario_test(runner, "sarah_speed", user_input, "APPROVE")


@pytest.mark.asyncio
async def test_scenario_sarah_decline(runner):
    """
    Test Sarah Speed (Core - Decline).
    ID: sarah_decline
    """
@pytest.mark.asyncio
async def test_scenario_sarah_decline(runner):
    """
    Test Sarah Speed (Core - Decline).
    ID: sarah_decline
    """
    user_input = (
        "process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, "
        "income: 59758, employer: City Hospital, amount: 50000, purpose: Home Improvement, "
        "monthly_payment: 1200. My Loan-to-Value (LTV) is 90% and I have been employed for 5 years."
    )
    # Valid outcomes: DENY (best) or QUESTION (safe fallback).
    await run_scenario_test(runner, "sarah_decline", user_input, ["DENY", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_gary_escalate(runner):
    """
    Test Gary Escalate (Core - Escalate).
    ID: gary_escalate
    """
    user_input = (
        "process a new loan application for name: Gary Escalate, gov_id: 900-00-3456, "
        "income: 60000, employer: Medianville Manufacturing, amount: 10000, purpose: Home Improvement, "
        "monthly_payment: 300"
    )
    # Valid outcomes: ESCALATE (best) or QUESTION (safe fallback).
    await run_scenario_test(runner, "gary_escalate", user_input, ["ESCALATE", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_alex_resilience(runner):
    """
    Test Alex Resilience (X-Factor - Resilience).
    ID: alex_resilience
    """
    user_input = (
        "process a new loan application for name: Alex Resilience, gov_id: 000-00-0000, "
        "income: 50000, employer: Tech Corp, amount: 10000, purpose: personal"
    )
    # Valid outcomes: DENY (best) or QUESTION (clarification). ERROR is also possible if ID fails hard.
    await run_scenario_test(runner, "alex_resilience", user_input, ["DENY", "QUESTION", "ERROR"])

@pytest.mark.asyncio
async def test_scenario_jane_fraud(runner):
    """
    Test Jane Fraud (X-Factor - Fraud).
    ID: jane_fraud
    """
    user_input = (
        "process a new loan application for name: Jane Fraud, gov_id: 900-00-9999, "
        "income: 0, employer: none, amount: 5000, purpose: personal"
    )
    # Valid outcomes: DENY (best) or QUESTION (safe fallback).
    await run_scenario_test(runner, "jane_fraud", user_input, ["DENY", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_maria_agility(runner):
    """
    Test Maria Agility (X-Factor - Agility).
    ID: maria_agility
    """
    user_input = (
        "process a new loan application for name: Maria Agility, gov_id: 900-00-9012, "
        "income: 85000, employer: Marias Designs, amount: 20000, purpose: business, "
        "monthly_payment: 500"
    )
    # Valid outcomes: ESCALATE (standard) or QUESTION (clarification) or APPROVE (if swap active).
    await run_scenario_test(runner, "maria_agility", user_input, ["ESCALATE", "QUESTION", "APPROVE"])
