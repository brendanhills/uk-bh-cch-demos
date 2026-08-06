from google.adk.agents.llm_agent import Agent
from typing import Any
from google.adk.tools.long_running_tool import LongRunningFunctionTool

# 1. Define the long running function
def ask_for_approval(
    purpose: str, amount: float
) -> dict[str, Any]:
  """Ask for approval for the reimbursement."""
  # create a ticket for the approval
  # Send a notification to the approver with the link of the ticket
  return {
      'status': 'pending',
      'approver': 'Chandrika',
      'purpose': purpose,
      'amount': amount,
      'ticket-id': 'approval-ticket-1',
  }

def reimburse(purpose: str, amount: float) -> str:
    """Reimburse the amount of money to the employee."""
    # send the reimbrusement request to payment vendor
    return {'status': 'ok'}

# 2. Wrap the function with LongRunningFunctionTool
long_running_tool = LongRunningFunctionTool(func=ask_for_approval)


finance_agent = Agent(
    model='gemini-2.5-flash',
    name='finance_agent',
    instruction='You handle employee expenses. If an expense requires approval, ask for it. Once approved, reimburse the employee. Use tool long_running_tool to initiate asking for approval. Use reimburse tool to activate approval',
    tools=[
        long_running_tool, 
        reimburse
    ]
)