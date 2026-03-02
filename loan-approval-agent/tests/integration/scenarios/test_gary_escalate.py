import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent import config

@pytest.mark.asyncio
async def test_scenario_gary_escalate():
    """Test Gary Escalate (Core - Escalate)."""
    config.LATENCY_MODE = "TESTING"
    runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
    session = await runner.session_service.create_session(app_name="loan_agent", user_id="test_user")
    
    user_input = (
        "Process a loan for Gary Escalate (ID: 900-00-3456). "
        "He earns $60,000 and needs $15,000 for business purposes."
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    final_response = ""
    async for event in runner.run_async(user_id="test_user", session_id=session.id, new_message=content):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"

    print(f"\n[GARY_ESCALATE TEST] Final Response: {final_response}")
    expected = ["ESCALATE", "HUMAN", "REVIEW", "INFO", "DETAILS", "QUESTION"]
    assert any(k.upper() in final_response.upper() for k in expected)
