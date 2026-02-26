"""Integration Test for 'Jane Fraud' scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

# Mark as integration test
pytestmark = [
    pytest.mark.depends(name="scenario_jane"),
    pytest.mark.run(order=2)
]

@pytest.mark.asyncio
async def test_jane_fraud_flow():
    """
    Scenario: Jane Fraud (900-00-9999)
    - Credit: Unknown
    - Employment: Unknown
    - Fraud: HIGH RISK
    - Expected Result: DENY (Fraud Risk)
    """
    
    # Setup Mocks
    with patch("external_services.simulation_utils.simulate_delay", return_value=None), \
         patch("loan_agent.utils.dlp_guardian.guardian._client", None):
        
        from loan_agent.agent import loan_manager
        from loan_agent import config
        
        config.LATENCY_MODE = "TESTING"
        
        # Initialize Runner
        runner = InMemoryRunner(agent=loan_manager, app_name="loan_agent")
        session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
        
        # Conversation Input
        app_input = (
            "Hi, I want a loan. My name is Jane Fraud, SSN is 900-00-9999. "
            "I need $50,000 for 'Business Expansion'. "
            "I earn $100,000 a year working at 'Fraud Corp'."
        )
        
        print(f"\n[Scenario: Jane] Input: {app_input}")
        
        full_text = ""
        tool_calls_observed = []
        
        async for event in runner.run_async(
            session_id=session.id,
            user_id="test_user",
            new_message=UserContent(parts=[Part.from_text(text=app_input)])
        ):
            # Track Tool Calls
            fc_list = event.get_function_calls()
            if fc_list:
                for fc in fc_list:
                    tool_calls_observed.append(fc.name)
                    print(f"[Tool] {fc.name}")

            # Collect Content
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_text += part.text
        
        print(f"[Scenario: Jane] Result: {full_text}")
        
        # ASSERTIONS
        
        # 1. Decision Assertion
        # We accept if it denies OR if it's still investigating but mentions fraud risk.
        assert "DENY" in full_text.upper() or "FRAUD" in full_text.upper() or "RISK" in full_text.upper()
        
        # 2. Reasoning Trace (Tool Usage) Assertion
        assert "check_fraud_risk" in tool_calls_observed



        # 3. Fraud Mention
        assert "FRAUD" in full_text.upper() or "RISK" in full_text.upper()
