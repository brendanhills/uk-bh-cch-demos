
"""Integration tests for Loan Approval Agent"""
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
import dotenv

@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()

@pytest.mark.asyncio
async def test_demo_core():
    """Test core demo scenarios (Sarah Jenkins)."""
    await AgentEvaluator.evaluate(
        agent_module="loan_approval_agent",
        eval_dataset_file_path_or_dir="loan_approval_agent/eval/eval_set_demo_core.json",
    )

@pytest.mark.asyncio
async def test_demo_edge():
    """Test edge case scenarios (Gary, Jane)."""
    await AgentEvaluator.evaluate(
        agent_module="loan_approval_agent",
        eval_dataset_file_path_or_dir="loan_approval_agent/eval/eval_set_demo_edge.json",
    )

@pytest.mark.asyncio
async def test_regression():
    """Test regression scenarios (David Yacht)."""
    await AgentEvaluator.evaluate(
        agent_module="loan_approval_agent",
        eval_dataset_file_path_or_dir="loan_approval_agent/eval/eval_set_regression.json",
    )
