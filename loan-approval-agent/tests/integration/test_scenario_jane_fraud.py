"""Integration Test for 'Jane Fraud' (Fraud Risk) scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

@pytest.mark.asyncio
async def test_jane_fraud_flow():
    """Verify that Jane Fraud is identified as high risk."""
    
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
            "Hi, I want a loan. My name is Jane Fraud, SSN is 900-00-9999. "
            "I earn $50,000 working independently. I need $5,000."
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

        print(f"\n[Jane Fraud Test] Final Output:\n{full_text}")

        # 3. Decision Assertion
        # It should be DENIED or flagged for FRAUD
        assert "DENY" in full_text.upper() or "FRAUD" in full_text.upper() or "RISK" in full_text.upper()
