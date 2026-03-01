"""End-to-End Integration Test for Loan Approval Agent."""
import pytest
import asyncio
from unittest.mock import patch
import os

@pytest.mark.asyncio
async def test_end_to_end_approval():
    """Verify full multi-agent flow from intake to decision for a valid applicant."""
    
    # Setup Mocks (Regex DLP)
    with patch("external_services.simulation_utils.simulate_delay", return_value=None), \
         patch("loan_agent.utils.dlp_guardian.guardian._client", None), \
         patch("loan_agent.utils.dlp_guardian.guardian._use_cloud_dlp_checked", True):
        
        # Move imports here to ensure patches apply if logic runs on import
        from google.adk.runners import InMemoryRunner
        from loan_agent.agent import loan_manager
        from google.genai.types import Part, UserContent

        # 1. Setup Runner
        runner = InMemoryRunner(agent=loan_manager)
        session = await runner.session_service.create_session(user_id="test_user", app_name="loan_agent")
        
        # 2. Start Conversation
        # Valid Sarah Speed Data
        app_input = (
            "Process a new loan application for Sarah Speed (ID: 900-00-1234). "
            "She earns $59,758 at City Hospital. She wants $20,000 for Debt Consolidation. "
            "Her monthly payment is $500."
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
                        full_text += part.text + " "
        
        print(f"\n[E2E] Final Text: {full_text}")
        
        # 3. Assertions
        assert len(full_text) > 100
        assert "ERROR" not in full_text.upper()
        assert "APPROVE" in full_text.upper() or "APPROVED" in full_text.upper()
