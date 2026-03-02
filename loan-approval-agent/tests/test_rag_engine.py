import pytest
import os
from unittest.mock import patch, MagicMock
from loan_agent.sub_agents.policy_expert.tools import consult_policy_docs

# Mark as unit test dependency
pytestmark = [
    pytest.mark.depends(name="unit_tests"),
    pytest.mark.run(order=1)
]

def test_rag_engine_sarah_decline_query():
    """
    Verify RAG retrieves the strict $150k income / 35% DTI rules for Sarah's $50k request.
    """
    query = "Standard Underwriting Guidelines 2026 high value restrictions"
    try:
        result = consult_policy_docs(query, applicant_id="TEST_SARAH_DECLINE")
        
        # Check for expected content
        assert "Hybrid RAG Search Results" in result
        assert "CITATION:" in result
        
        # Check for the specific rules we added to the 2026 Guidelines
        assert "150000" in result
        assert "35 PERCENT" in result
        
        print(f"\n[RAG Sarah Test] Successfully retrieved mandatory high-value rules.")
        
    except Exception as e:
        pytest.fail(f"RAG failed to retrieve Sarah's decline rules: {e}")

def test_rag_engine_gary_escalate_query():
    """
    Verify RAG retrieves manual review requirements for Tier 3 applicants.
    """
    query = "Standard Underwriting Guidelines 2026 credit score tiers"
    try:
        result = consult_policy_docs(query, applicant_id="TEST_GARY_ESCALATE")
        
        assert "Hybrid RAG Search Results" in result
        # Check for credit tier rules
        assert "Tier 3" in result
        assert "Manual Review" in result
        
        print(f"\n[RAG Gary Test] Successfully retrieved Tier 3 review rules.")
        
    except Exception as e:
        pytest.fail(f"RAG failed to retrieve Gary's escalation rules: {e}")

def test_rag_engine_mock_retrieval():
    """Verify the formatting logic of consult_policy_docs using mocks."""
    
    # Mock the RAG retrieval response
    mock_context = MagicMock()
    mock_context.text = "Mocked policy text about DTI."
    mock_context.source_uri = "gs://test-bucket/test_policy.pdf"
    
    # The structure is response.contexts.contexts (a list)
    mock_contexts_obj = MagicMock()
    mock_contexts_obj.contexts = [mock_context]
    
    mock_response = MagicMock()
    mock_response.contexts = mock_contexts_obj
    
    with patch("vertexai.preview.rag.retrieval_query", return_value=mock_response), \
         patch("vertexai.init"):
        
        result = consult_policy_docs("DTI limits", applicant_id="TEST_RAG_MOCK")
        
        assert "Hybrid RAG Search Results" in result
        assert "CITATION: gs://test-bucket/test_policy.pdf" in result
        assert "Mocked policy text about DTI." in result
