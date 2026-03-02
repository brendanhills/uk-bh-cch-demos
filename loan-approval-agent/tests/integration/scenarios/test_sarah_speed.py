import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent import config

@pytest.mark.asyncio
async def test_scenario_sarah_speed():
    """Test Sarah Speed (Core - Auto-Approve)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "Please process a loan application for Sarah Speed (ID: 900-00-1234). "
        "She wants $20,000 for Debt Consolidation. She earns $59,758 at City Hospital. "
        "Her monthly current debt payment is $500."
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[SARAH_SPEED TEST] Final Response: {final_response}")
    expected = ["APPROVE", "SUCCESS", "REQUEST_INFO"]
    assert any(k.upper() in final_response.upper() for k in expected)

@pytest.mark.asyncio
async def test_scenario_sarah_decline():
    """Test Sarah Speed (Edge - High Value Restriction)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "process a new loan application for Sarah Speed, gov_id: 900-00-1234, "
        "income: 59758, employer: City Hospital, amount: 50000, purpose: Luxury Home Improvement, "
        "monthly_payment: 1200"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[SARAH_DECLINE TEST] Final Response: {final_response}")
    expected = ["DENY", "ESCALATE"]
    assert any(k.upper() in final_response.upper() for k in expected)
