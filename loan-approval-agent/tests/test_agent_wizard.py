import pytest
import asyncio
from google.genai.types import Part, UserContent
from google.adk.runners import InMemoryRunner
from loan_agent.agent import loan_manager

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

from loan_agent import config
# Set latency to testing mode for speed
config.LATENCY_MODE = "TESTING"

@pytest.mark.asyncio
async def test_orchestrator_wizard_input():
    """Test that the Orchestrator correctly parses the input format from the Wizard."""
    # This input mimics what demo_app.py constructs
    user_input = (
        "Begin review for applicant_id: 12345. "
        "Requested Loan Amount: $50,000. "
        "Stated Income: $60,000. "
        "Loan Purpose: Home Improvement."
    )
    
    # Run the agent with this input
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = UserContent(parts=[Part(text=user_input)])
    
    responses = []
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_user",
        new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    responses.append(part.text)

    final_response = " ".join(responses)
    
    # Check that it extracted the ID and started the investigation (or asked for more info)
    assert "12345" in final_response or "Applicant ID" in final_response
    assert len(final_response) > 50
