
import pytest
import pytest_asyncio
import os
import sys
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part
from loan_approval_agent.agent import loan_manager
import dotenv

# Load environment variables
dotenv.load_dotenv()

@pytest_asyncio.fixture
async def runner():
    """Fixture to provide an InMemoryRunner instance."""
    runner = InMemoryRunner(agent=loan_manager)
    return runner

async def run_scenario_test(runner, name, user_input, expected_outcome):
    """Helper function to run a scenario and assert the outcome."""
    print(f"\n--- Running Test Scenario: {name} ---")
    
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id=f"test_user_{name.lower().replace(' ', '_')}"
    )
    
    content = UserContent(parts=[Part(text=user_input)])
    
    final_response = ""
    
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text + "\n"
                    print(f"AGENT: {part.text}")
        elif event.tool_response:
            # Capture tool output if helpful for debugging, or just ignore
            pass
        elif event.exception:
            print(f"EXCEPTION: {event.exception}")


    print(f"Final Response: {final_response}")
    
    # Assert
    assert expected_outcome in final_response.upper(), f"Expected '{expected_outcome}' in response, but got: {final_response}"

@pytest.mark.asyncio
async def test_scenario_sarah_jenkins_approve(runner):
    """
    Test Sarah Jenkins (Core - Approve).
    Requires correct Tokenization and DTI calculation.
    """
    # Use a clear, structured prompt to ensure all fields are captured
    user_input = (
        "I want to register a new loan application. \n"
        "Applicant Name: Sarah Jenkins\n"
        "Government ID: 900-00-1234\n"
        "Annual Income: 59758\n"
        "Employer: City Hospital\n"
        "Loan Amount: 20000\n"
        "Loan Purpose: Debt Consolidation\n"
        "Loan Duration: 60 months\n"
        "Estimated New Loan Monthly Payment: 380\n"
    )
    await run_scenario_test(runner, "Sarah Jenkins", user_input, "APPROVE")

@pytest.mark.asyncio
async def test_scenario_gary_gray_escalate(runner):
    """
    Test Gary Gray (Edge - Escalate).
    Requires Risk Analysis to flag Borderline Credit or High Debt.
    """
    user_input = (
        "I want to register a new loan application. \n"
        "Applicant Name: Gary Gray\n"
        "Government ID: 900-00-3456\n"
        "Annual Income: 60000\n"
        "Employer: Medianville Manufacturing\n"
        "Loan Amount: 10000\n"
        "Loan Purpose: Home Improvement\n"
    )
    await run_scenario_test(runner, "Gary Gray", user_input, "ESCALATE")
