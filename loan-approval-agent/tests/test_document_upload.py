import pytest
import asyncio
import os
import shutil
from unittest.mock import patch, MagicMock

# Mark as unit test dependency
pytestmark = [
    pytest.mark.dependency(name="unit_upload"),
    pytest.mark.run(order=1)
]

from google.genai.types import (
    UserContent, Part, GenerateContentResponse, Candidate, Content, FunctionCall
)
from google.adk.runners import InMemoryRunner
from loan_agent.agent import loan_manager
from loan_agent.sub_agents.investigator.agent import investigator_agent
from loan_agent import config

# Use TESTING latency
config.LATENCY_MODE = "TESTING"

def create_mock_response(text=None, function_calls=None):
    parts = []
    if text:
        parts.append(Part(text=text))
    if function_calls:
        for fc in function_calls:
            # FunctionCall args must be dict
            parts.append(Part(function_call=FunctionCall(name=fc.name, args=fc.args)))
            
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
@pytest.mark.skip(reason="Legacy test targeting loan_agent. Needs migration to loan_agent and doc_analyzer.")
@patch("loan_agent.tools.doc_analyzer.Client")
async def test_document_upload_analysis(MockClient, capsys):
    """Verifies that the agent analyzes uploaded documents when provided."""
    
    # Setup mock response for the Tool (Client)
    mock_instance = MockClient.return_value
    mock_response = MagicMock()
    mock_response.text = '{"income": 80000, "employer": "Tech Giant Corp", "consistency": "high"}'
    mock_instance.models.generate_content.return_value = mock_response

    # Ensure mock docs exist
    upload_dir = "artifacts/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    payslip_path = os.path.join(upload_dir, "mock_payslip.pdf")
    bank_path = os.path.join(upload_dir, "mock_bank_statement.pdf")
    
    # Create dummy files if they don't exist
    with open(payslip_path, "wb") as f:
        f.write(b"dummy pdf content")
    with open(bank_path, "wb") as f:
        f.write(b"dummy pdf content")

    # Mock the Agent Models to avoid network calls and infinite loops
    from unittest.mock import AsyncMock
    
    mock_orch_model = AsyncMock()
    mock_inv_model = AsyncMock()
    
    # We need to mock registry.resolve because LlmAgent resolves the model name string to a class
    # and then instantiates it.
    
    # Orchestrator calls investigator_agent
    mock_orch_model.generate_content_async.return_value = create_mock_response(
        function_calls=[FunctionCall(name="investigator_agent", args={
             "loan_amount": 10000,
             "loan_purpose": "Home Improvement",
             "stated_income": 80000,
             "application_id": "APP-TEST",
             "monthly_payment": 500
        })]
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

    # Create a mock for the Registry resolve
    with patch("google.adk.models.registry.LLMRegistry.resolve") as mock_resolve:
        MockOrchClass = MagicMock(return_value=mock_orch_model)
        MockInvClass = MagicMock(return_value=mock_inv_model)
        
        def resolve_side_effect(model_name):
            # Simplistic check
            if "investigator" in model_name or "flash" in model_name:
                 return MockInvClass
            return MockOrchClass

        mock_resolve.side_effect = resolve_side_effect
        
        # Override agent models to ensure they use strings that trigger our mock
        loan_manager.model.model = "gemini-2.5-pro"
        investigator_agent.model.model = "gemini-2.5-flash"

        runner = InMemoryRunner(agent=loan_manager, app_name="agents")
        session = await runner.session_service.create_session(app_name="agents", user_id="test_user")

        # Simulate applicant with documents
        applicant_id = "900-00-1234"
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
            
            if analyzed_docs or step_count > 5:
                break
                            
        assert analyzed_docs, "Agent did not choose to call analyze_document"
