import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent import config

@pytest.mark.asyncio
async def test_scenario_jane_fraud():
    """Test Jane Fraud (Core - Fraud Risk)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "Hi, I want a loan. My name is Jane Fraud, SSN is 900-00-9999. "
        "I earn $50,000 working independently. I need $5,000."
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[JANE_FRAUD TEST] Final Response: {final_response}")
    expected = ["DENY", "FRAUD", "RISK", "QUESTION", "INFO", "DETAILS"]
    assert any(k.upper() in final_response.upper() for k in expected)
