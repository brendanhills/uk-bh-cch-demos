import pytest
import asyncio
from unittest.mock import patch, MagicMock
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager
from loan_agent.sub_agents.investigator.agent import investigator_agent

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_document_upload_flow():
    """Verify that the agent can handle document upload triggers."""
    
    # 1. Setup Runner
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user")
    
    # 2. Simulate User with PII and mention of document
    user_input = (
        "Hi, I am Sarah Speed. ID 900-00-1234. I earn $60,000. "
        "I've uploaded my paystub for verification. Please process my $20,000 loan."
    )
    
    # 3. Mock the document tool response to avoid real vision call
    with patch("loan_agent.sub_agents.investigator.tools.analyze_document", return_value={"employer_name": "City Hospital", "gross_pay": 5000}):
        responses = []
        async for event in runner.run_async(
            session_id=session.id,
            user_id="test_user",
            new_message=UserContent(parts=[Part(text=user_input)])
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        responses.append(part.text)

    final_response = " ".join(responses)
    # The agent should at least start or mention something related to the application
    assert len(final_response) > 50
    assert "application" in final_response.lower() or "registered" in final_response.lower()
