import pytest
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_qa_missing_info():
    """
    Test that the agent asks a clarifying question when 'Employer' is Unknown.
    Uses mock applicant 12349.
    """
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_qa_user"
    )

    # Input for Jane Fraud (12349) with "Unknown" employer
    user_input = (
        "Begin review for applicant_id: 12349. "
        "I earn $50,000. I want $5,000. My ID is 900-00-9999."
    )
    
    responses = []
    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_qa_user",
        new_message=UserContent(parts=[Part(text=user_input)])
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    responses.append(part.text)

    final_response = " ".join(responses)
    
    # It should ask about the employer or missing fields
    assert "?" in final_response or "employer" in final_response.lower() or "provide" in final_response.lower()
