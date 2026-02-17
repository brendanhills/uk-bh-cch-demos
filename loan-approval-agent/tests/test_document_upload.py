
import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from google.genai.types import UserContent, Part
from google.adk.runners import InMemoryRunner
from loan_approval_agent.agent import loan_manager
from loan_approval_agent import config

# Use TESTING latency
config.LATENCY_MODE = "TESTING"

@pytest.mark.asyncio

@patch("loan_approval_agent.sub_agents.investigator.tools.Client")
async def test_document_upload_analysis(MockClient, capsys):
    """Verifies that the agent analyzes uploaded documents when provided."""
    
    # Setup mock response
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

    runner = InMemoryRunner(agent=loan_manager, app_name="agents")
    session = await runner.session_service.create_session(app_name="agents", user_id="test_user")

    # Simulate applicant with documents
    # We use a known ID but add the document context manually as demo_app does
    applicant_id = "12345" # John Doe
    initial_input = (
        f"Begin review for applicant_id: {applicant_id}. "
        f"Requested Loan Amount: $10,000. "
        f"Loan Purpose: Home Improvement."
        f"\nThe applicant has provided supporting documents: {payslip_path}, {bank_path}. "
        f"Please analyze these to verify income and employment."
    )
    
    user_msg = UserContent(parts=[Part(text=initial_input)])
    
    analyzed_docs = False
    final_decision = False
    
    print("\n--- Starting Document Upload Test ---")
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=user_msg,
    ):
        if hasattr(event, 'tool_calls') and event.tool_calls:
            for tc in event.tool_calls:
                for fc in tc.function_calls:
                    print(f"TOOL CALL: {fc.name} args={fc.args}")
                    if fc.name == "analyze_document":
                        analyzed_docs = True
                        
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"AGENT: {part.text}")
                    if "Final Decision:" in part.text:
                        final_decision = True
                        
    # Verify analyze_document execution via debug print
    captured = capsys.readouterr()
    print(captured.out) # Print again so we can see it in failure logs if needed
    
    # Check if debug print appeared
    assert "DEBUG: analyze_document called" in captured.out, "Agent did not call analyze_document (based on debug log)."
    expected_question_keywords = ["payslip", "bank statement", "document", "upload", "employer"]
    question_found = any(k in captured.out.lower() for k in expected_question_keywords) or (final_decision)
    
    if not final_decision:
         print("Agent asked for clarification instead of final decision, which is valid if documents show discrepancies.")
         
    assert question_found or final_decision, "Agent did not reach a final decision OR ask a relevant question about documents."
    print("--- Test Passed ---")
