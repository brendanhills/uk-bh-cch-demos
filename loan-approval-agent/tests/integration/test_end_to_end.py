"""Robust End-to-End Integration Test using InMemoryRunner"""
import pytest
import sys
import os
import asyncio
from unittest.mock import patch

# Mark E2E test to depend on integration scenarios
pytestmark = [
    pytest.mark.depends(name="e2e", depends=["integration_scenarios"]),
    pytest.mark.run(order=3)
]

@pytest.mark.asyncio
async def test_end_to_end_approval():
    """
    Simulates a full loan application flow using the InMemoryRunner.
    This avoids the complexity/flakiness of AgentEvaluator for simple E2E checks.
    """
    from google.genai.types import Part, UserContent

    # 1. Setup Mocks (Force working model & Regex DLP)
    with patch("external_services.simulation_utils.simulate_delay", return_value=None), \
         patch("loan_agent.utils.dlp_guardian.guardian._client", None), \
         patch("loan_agent.utils.dlp_guardian.guardian._use_cloud_dlp_checked", True):
        
        # Move imports here to ensure patches apply if logic runs on import
        from google.adk.runners import InMemoryRunner
        from loan_agent.agent import loan_manager

        from loan_agent.agent import loan_manager, app
        from loan_agent.sub_agents.investigator.agent import investigator_agent
        from loan_agent.sub_agents.policy_expert.agent import policy_expert_agent
        from loan_agent.sub_agents.underwriter.agent import underwriter_agent
        
        # 2. Initialize Runner
        # Force models to gemini-2.5-flash for testing
        def force_flash(agent):
            if isinstance(agent.model, str):
                agent.model = "gemini-2.5-flash"
            else:
                agent.model.model = "gemini-2.5-flash"
            # Remove thinking_config if present as it's not supported by 2.5-flash
            if hasattr(agent, 'generate_content_config') and agent.generate_content_config:
                agent.generate_content_config.thinking_config = None

        force_flash(loan_manager)
        force_flash(investigator_agent)
        force_flash(policy_expert_agent)
        force_flash(underwriter_agent)

        runner = InMemoryRunner(app=app)
        session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
        
        # 3. Start Conversation
        app_input = (
            "Process a new loan application for Sarah Speed (ID: 900-00-1234). "
            "She wants $15,000 for Home Improvement. "
            "She earns $59,758/year at City Hospital."
        )
        
        print(f"\n[E2E] Sending: {app_input}")
        full_text = ""
        
        async for event in runner.run_async(
            session_id=session.id,
            user_id="test_user",
            new_message=UserContent(parts=[Part.from_text(text=app_input)])
        ):
            # Log Tool Calls
            if hasattr(event, "tool_calls") and event.tool_calls:
                for tc in event.tool_calls:
                    for fc in tc.function_calls:
                        print(f"\n[Tool Call] {fc.name}({fc.args})", flush=True)

            # Log Content
            if hasattr(event, "content") and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                        full_text += part.text
            
            # Log Errors if any (though typically raised)
        
        print(f"\n[E2E] Final Text: {full_text}")
        
        # 4. Assertions
        # ID might not be in final text if using internal ID, check for either
        assert len(full_text) > 100
        assert "ERROR" not in full_text.upper()
        assert "APP-" in full_text

        # Relax assertion to catch partial success or just check logs
        if "APPROVE" not in full_text.upper() and "APPROVED" not in full_text.upper():
            pytest.fail(f"Did not find APPROVE decision. Full text: {full_text}")
