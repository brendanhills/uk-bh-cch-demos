import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent import config

@pytest.mark.asyncio
async def test_scenario_jane_fraud_intake():
    """
    Test Jane Fraud (Scenario 4) - Conversational Intake.
    Verifies that the agent asks for missing info (employer) and remembers context.
    """
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    # Message 1: Missing Employer
    user_input_1 = "Hi, I'm Jane Fraud. SSN 900-00-9999. I earn $0. I want $5,000 for personal use."
    content_1 = UserContent(parts=[Part(text=user_input_1)])
    
    resp_1 = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content_1):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    resp_1 += part.text

    print(f"\n[Jane Intake Turn 1] Response: {resp_1}")
    # Agent should ask for employer
    assert "employer" in resp_1.lower() or "work" in resp_1.lower()

    # Message 2: Providing "No employer"
    user_input_2 = "No employer."
    content_2 = UserContent(parts=[Part(text=user_input_2)])
    
    resp_2 = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content_2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    resp_2 += part.text

    print(f"\n[Jane Intake Turn 2] Response: {resp_2}")
    
    # Once complete, it should trigger investigation and ultimately DENY (Fraud)
    # The response should mention the investigation and/or the final fraud decision.
    expected = ["DENY", "FRAUD", "RISK", "INVESTIGATION", "REJECT"]
    assert any(k.upper() in resp_2.upper() for k in expected)
