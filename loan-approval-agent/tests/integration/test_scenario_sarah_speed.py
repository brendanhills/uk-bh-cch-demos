"""Integration Test for 'Sarah Speed' (Auto-Approve) scenario."""
import pytest
import asyncio
from unittest.mock import patch
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

# Mark as integration test
pytestmark = [
    pytest.mark.depends(name="scenario_sarah"),
    pytest.mark.run(order=2)
]

@pytest.mark.asyncio
async def test_sarah_speed_auto_approve():
    """
    Scenario: Sarah Speed (900-00-1234)
    - Credit: Excellent (725)
    - Employment: Verified (City Hospital, $59,758)
    - Fraud: Low Risk
    - Policy: Within guidelines for $15,000
    - Expected Result: APPROVE
    """
    
    # Setup Mocks
    with patch("external_services.simulation_utils.simulate_delay", return_value=None), \
         patch("loan_agent.utils.dlp_guardian.guardian._client", None):
        
        from loan_agent.agent import loan_manager, app
        from loan_agent import config

        # Ensure we use testing mode for speed
        config.LATENCY_MODE = "TESTING"

        # Initialize Runner
        runner = InMemoryRunner(app=app)

        session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
        
        # Conversation Input
        app_input = (
            "Please process a loan application for Sarah Speed (ID: 900-00-1234). "
            "She is requesting $15,000 for 'Home Improvement'. "
            "She mentioned she works at City Hospital and earns around $60,000 per year."
        )
        
        print(f"\n[Scenario: Sarah] Input: {app_input}")
        
        full_text = ""
        tool_calls_observed = []
        
        async for event in runner.run_async(
            session_id=session.id,
            user_id="test_user",
            new_message=UserContent(parts=[Part.from_text(text=app_input)])
        ):
            # Track Tool Calls for "Reasoning Trace" verification
            # Use get_function_calls() for ADK Event objects
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
        
        print(f"[Scenario: Sarah] Result: {full_text}")
        
        # ASSERTIONS
        
        # 1. Decision Assertion
        assert "APPROVE" in full_text.upper() or "APPROVED" in full_text.upper()
        
        # 2. Reasoning Trace (Tool Usage) Assertion
        # With the handoff pattern, we should see the actual tools called by sub-agents.
        
        required_tools = [
            "get_credit_report",
            "consult_policy_docs",
            "record_decision"
        ]
        
        for tool in required_tools:
            assert tool in tool_calls_observed, f"Functional tool '{tool}' was not called during the process."


        # Additionally verify that the tools DID run by checking the final text or audit logs if needed.
        # But seeing the [ToolDispatcher] logs in stdout confirms they ran.


        # 3. Decision Assertion
        assert "APPROVE" in full_text.upper() or "APPROVED" in full_text.upper() or "SUCCESS" in full_text.upper()


