"""Integration Test for 'Gary Escalate' (Escalation) scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

# Mark as integration test
pytestmark = [
    pytest.mark.depends(name="scenario_gary"),
    pytest.mark.run(order=2)
]

@pytest.mark.asyncio
async def test_gary_escalate_flow():
    """
    Scenario: Gary Escalate (900-00-3456)
    - Credit: Moderate (650)
    - Employment: Verified (Medianville Manufacturing, $60,000, 8 years)
    - Debt: High (Divorce settlement) -> High DTI
    - Expected Result: ESCALATE
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
            "Process a loan for Gary Escalate (ID: 900-00-3456). "
            "He needs $25,000 for 'Debt Consolidation'. "
            "He works at Medianville Manufacturing and earns $60,000 per year."
        )
        
        print(f"\n[Scenario: Gary] Input: {app_input}")
        
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
        
        print(f"[Scenario: Gary] Result: {full_text}")
        
        # ASSERTIONS
        
        # 1. Decision Assertion
        assert "ESCALATE" in full_text.upper() or "HUMAN" in full_text.upper() or "REVIEW" in full_text.upper()
        
        # 2. Reasoning Trace (Tool Usage) Assertion
        # We check for at least some sub-tools being called.
        assert "get_credit_report" in tool_calls_observed or "consult_policy_docs" in tool_calls_observed


