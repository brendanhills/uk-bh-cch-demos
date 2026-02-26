
import pytest
import os
import sys
import asyncio
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

# Add project root to path
sys.path.append(os.getcwd())

from loan_agent import config
# Set latency to testing mode
config.LATENCY_MODE = "TESTING"

from loan_agent.agent import loan_manager


@pytest.mark.asyncio
async def test_orchestrator_wizard_input():
    """Test that the Orchestrator correctly parses the input format from the Wizard."""
    # This input mimics what demo_app.py constructs
    user_input = (
        "Begin review for applicant_id: 12345. "
        "Requested Loan Amount: $50,000. "
        "Loan Purpose: Home Improvement."
    )
    
    # Run the agent with this input
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=user_input)])
    
    # We collect the response to verify it
    final_response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text
    
    # Verification
    # The agent should have tried to investigate ID: 12345
    # Since 12345 is likely not in our Mock DB, it might return an error or "Not Found" logic.
    # But the KEY thing is that the Agent *attempted* to use the ID.
    # A successful test matches "12345" in the output trace or a specific error message about 12345.
    
    # Note: If the model is smart, it might say "I started investigation for 12345"
    assert "12345" in final_response or "Applicant ID" in final_response
    # It should also likely fail gracefully or make a decision based on limited info.
    # We just want to ensure it didn't crash or ignore the input.
    assert len(final_response) > 50
