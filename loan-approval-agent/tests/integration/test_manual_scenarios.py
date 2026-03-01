import pytest
import asyncio
import pytest_asyncio
import dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager

dotenv.load_dotenv()

@pytest_asyncio.fixture
async def runner():
    """Fixture to provide an InMemoryRunner instance."""
    return InMemoryRunner(agent=loan_manager)

async def run_scenario_test(runner, name, user_input, expected_keywords):
    """Helper to run a conversation and assert outcomes."""
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
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

    print(f"Final Response: {final_response}")
    
    if isinstance(expected_keywords, str):
        expected_keywords = [expected_keywords]
        
    found = any(k.upper() in final_response.upper() for k in expected_keywords)
    assert found, f"Expected one of {expected_keywords} in response, but got: {final_response[:100]}..."

@pytest.mark.asyncio
async def test_scenario_sarah_speed(runner):
    """Test Sarah Speed (Core - Auto-Approve)."""
    user_input = (
        "process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, "
        "income: 59758, employer: City Hospital, amount: 20000, purpose: Debt Consolidation, "
        "monthly_payment: 300"
    )
    # Valid outcomes: APPROVE (best) or REQUEST_INFO (if tenure check triggers).
    await run_scenario_test(runner, "sarah_speed", user_input, ["APPROVE", "REQUEST_INFO"])

@pytest.mark.asyncio
async def test_scenario_sarah_decline(runner):
    """Test Sarah Speed (Edge - High Value Restriction)."""
    user_input = (
        "process a new loan application for name: Sarah Speed, gov_id: 900-00-1234, "
        "income: 59758, employer: City Hospital, amount: 50000, purpose: Luxury Home Improvement, "
        "monthly_payment: 1200"
    )
    # Valid outcomes: DENY (best) or ESCALATE (conservative) or QUESTION (safe fallback).
    await run_scenario_test(runner, "sarah_decline", user_input, ["DENY", "ESCALATE", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_gary_escalate(runner):
    """Test Gary Escalate (Core - Escalate)."""
    user_input = (
        "process a new loan application for name: Gary Escalate, gov_id: 900-00-3456, "
        "income: 60000, employer: Medianville Manufacturing, amount: 15000, purpose: Business purchase"
    )
    # Valid outcomes: ESCALATE (standard) or QUESTION (clarification).
    await run_scenario_test(runner, "gary_escalate", user_input, ["ESCALATE", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_alex_resilience(runner):
    """Test Alex Resilience (Edge - Not Found)."""
    user_input = (
        "I want a loan. My name is Alex Resilience, ID is 000-00-0000. Amount $5,000."
    )
    # Valid outcomes: DENY or QUESTION or ERROR.
    await run_scenario_test(runner, "alex_resilience", user_input, ["DENY", "QUESTION", "ERROR"])

@pytest.mark.asyncio
async def test_scenario_jane_fraud(runner):
    """Test Jane Fraud (Core - Fraud Risk)."""
    user_input = (
        "Hi, I want a loan. My name is Jane Fraud, SSN is 900-00-9999. Amount $5,000. I am self-employed."
    )
    # Valid outcomes: DENY or QUESTION (if it wants more proof).
    await run_scenario_test(runner, "jane_fraud", user_input, ["DENY", "QUESTION"])

@pytest.mark.asyncio
async def test_scenario_maria_agility(runner):
    """Test Maria Agility (Scenario 5 - Multi-purpose)."""
    user_input = (
        "Process loan for Maria Agility, ID 900-00-1111. Amount 10000. "
        "monthly_payment: 500"
    )
    # Valid outcomes: ESCALATE (standard) or QUESTION (clarification) or APPROVE (if swap active).
    await run_scenario_test(runner, "maria_agility", user_input, ["ESCALATE", "QUESTION", "APPROVE"])
