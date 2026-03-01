"""Integration Test for 'Gary Escalate' (Escalation) scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

@pytest.mark.asyncio
async def test_gary_escalate_flow():
    """Verify that Gary Escalate triggers a manual review/escalation."""
    
    # Setup Mocks
    with patch("external_services.simulation_utils.simulate_delay", return_value=None):
        from loan_agent.agent import loan_manager
        from loan_agent import config

        config.LATENCY_MODE = "TESTING"

        # Initialize Runner
        runner = InMemoryRunner(agent=loan_manager)
        session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
        
        # Conversation Input
        app_input = (
            "Process a loan for Gary Escalate (ID: 900-00-3456). "
            "He earns $60,000 and needs $15,000 for business purposes."
        )
        
        user_content = UserContent(parts=[Part(text=app_input)])
        
        full_text = ""
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=user_content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_text += part.text + "\n"

        print(f"\n[Gary Escalate Test] Final Output:\n{full_text}")

        # 3. Decision Assertion
        # It should be ESCALATED or recommended for REVIEW
        assert "ESCALATE" in full_text.upper() or "HUMAN" in full_text.upper() or "REVIEW" in full_text.upper()
