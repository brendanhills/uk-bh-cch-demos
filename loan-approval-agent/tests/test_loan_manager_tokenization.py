import pytest
import asyncio
from unittest.mock import patch, MagicMock
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_agent.agent import loan_manager

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

@pytest.mark.asyncio
async def test_loan_manager_tokenization_flow():
    """Verify that the Loan Manager correctly tokenizes Gov ID before tools see it."""
    
    # 1. Setup Runner
    runner = InMemoryRunner(agent=loan_manager)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="test_user")
    
    # 2. User Input with PII
    user_input = (
        "Process a new loan application for name: Gary Escalate, "
        "gov_id: 900-00-3456, income: 60000, employer: Medianville Manufacturing, "
        "amount: 15000, purpose: Business"
    )
    
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

    # 3. Check State
    # The session state should now have an applicant_id which is NOT the SSN
    state = await runner.session_service.get_session(runner.app_name, session.id)
    applicant_id = state.state.get("applicant_id")
    assert applicant_id is not None
    assert applicant_id != "900-00-3456"
    assert applicant_id.startswith("user_")
