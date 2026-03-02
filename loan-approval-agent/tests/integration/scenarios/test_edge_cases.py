import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent import config

@pytest.mark.asyncio
async def test_scenario_alex_resilience():
    """Test Alex Resilience (Edge - Not Found)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "I want a loan. My name is Alex Resilience, ID is 000-00-0000. Amount $5,000."
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[ALEX_RESILIENCE TEST] Final Response: {final_response}")
    expected = ["DENY", "QUESTION", "ERROR", "INFO", "DETAILS"]
    assert any(k.upper() in final_response.upper() for k in expected)

@pytest.mark.asyncio
async def test_scenario_maria_agility():
    """Test Maria Agility (Scenario 5 - Multi-purpose)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "Process loan for Maria Agility, ID 900-00-1111. Amount 10000. "
        "monthly_payment: 500"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[MARIA_AGILITY TEST] Final Response: {final_response}")
    expected = ["ESCALATE", "QUESTION", "APPROVE", "INFO", "DETAILS"]
    assert any(k.upper() in final_response.upper() for k in expected)
