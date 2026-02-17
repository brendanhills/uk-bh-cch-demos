
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from google.genai.types import (
    UserContent, Part, GenerateContentResponse, Candidate, Content, FunctionCall
)
from google.adk.runners import InMemoryRunner
from loan_approval_agent.agent import loan_manager
from loan_approval_agent.sub_agents.investigator.agent import investigator_agent
from loan_approval_agent import config

# Use TESTING latency
config.LATENCY_MODE = "TESTING"

def create_mock_response(text=None, function_calls=None):
    parts = []
    if text:
        parts.append(Part(text=text))
    if function_calls:
        for fc in function_calls:
            parts.append(Part(function_call=fc))
            
    return GenerateContentResponse(
        candidates=[
            Candidate(
                content=Content(
                    parts=parts,
                    role="model"
                )
            )
        ]
    )

@pytest.mark.asyncio
@patch("loan_approval_agent.sub_agents.investigator.tools.Client")
async def test_document_upload_analysis(MockClient, capsys):
    """Verifies that the agent analyzes uploaded documents when provided."""
    
    # Setup mock response for the Tool (Client)
    mock_instance = MockClient.return_value
    mock_response = MagicMock()
    mock_response.text = '{"income": 80000, "employer": "Tech Giant Corp", "consistency": "high"}'
    mock_instance.models.generate_content.return_value = mock_response

    # Ensure mock docs exist
    upload_dir = "artifacts/uploads"
    payslip_path = os.path.join(upload_dir, "mock_payslip.pdf")
    bank_path = os.path.join(upload_dir, "mock_bank_statement.pdf")
    
    if not os.path.exists(payslip_path) or not os.path.exists(bank_path):
        pytest.skip("Mock documents not found. Run generate_mock_docs.py first.")


    # Mock the Agent Models to avoid network calls and infinite loops
    # Replace the model objects with AsyncMock directly
    from unittest.mock import AsyncMock
    
    mock_orch_model = AsyncMock()
    loan_manager.model = mock_orch_model
    
    mock_inv_model = AsyncMock()
    investigator_agent.model = mock_inv_model
    
    # Orchestrator calls investigator_agent
    mock_orch_model.generate_content_async.return_value = create_mock_response(
        function_calls=[FunctionCall(name="investigator_agent", args={})]
    )
    
    # Investigator calls analyze_document then returns analysis
    mock_inv_model.generate_content_async.side_effect = [
        # First turn: decide to call tool
        create_mock_response(
            function_calls=[
                FunctionCall(
                    name="analyze_document", 
                    args={"file_path": payslip_path, "query": "verify income"}
                )
            ]
        ),
        # Second turn: Process tool output and return summary
        create_mock_response(text="Analysis complete. Income verified.")
    ]
        


    runner = InMemoryRunner(agent=loan_manager, app_name="agents")
    session = await runner.session_service.create_session(app_name="agents", user_id="test_user")

    # Simulate applicant with documents
    applicant_id = "12345"
    initial_input = (
        f"Begin review for applicant_id: {applicant_id}. "
        f"Requested Loan Amount: $10,000. "
        f"Loan Purpose: Home Improvement."
        f"\nThe applicant has provided supporting documents: {payslip_path}, {bank_path}. "
        f"Please analyze these to verify income and employment."
    )
    
    user_msg = UserContent(parts=[Part(text=initial_input)])
    
    analyzed_docs = False
    
    print("\n--- Starting Document Upload Test ---")
    # We only run for a few turns to verify the tool call
    step_count = 0
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_msg,
    ):
        step_count += 1
        if hasattr(event, 'tool_calls') and event.tool_calls:
            for tc in event.tool_calls:
                for fc in tc.function_calls:
                    print(f"TOOL CALL: {fc.name} args={fc.args}")
                    if fc.name == "analyze_document":
                        analyzed_docs = True
        
        # Break early once we've seen enough
        if analyzed_docs or step_count > 5:
            break
                        
    # Verify analyze_document execution via debug print
    captured = capsys.readouterr()
    # print(captured.out) # Only print if needed
    
    # Verify that we actually mocked the response correctly and the tool was called
    # Note: InMemoryRunner might not actually call the tool if we intercept the model response 
    # BUT we want to verify the AGENT DECIDED to call the tool.
    # If we mock the model to return a function call, the Runner WILL try to execute it.
    # Since analyze_document is a real function (wrapped in tool), it will be executed.
    # And since we mocked Client inside it, it should run fine.
    
    assert analyzed_docs, "Agent did not choose to call analyze_document"
    assert "DEBUG: analyze_document called" in captured.out, "analyze_document implementation was not executed."
    print("--- Test Passed ---")
