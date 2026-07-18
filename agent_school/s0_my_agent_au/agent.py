from google.adk.agents.llm_agent import Agent
from .sub_agents import gce_subagent, gcs_subagent, finance_agent



root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Delegate user questions to the best sub agent to help the user answer their question.',
    instruction='Delegate user questions to the best sub agent to help the user answer their question.  Do not answer the question yourself.  ',
    sub_agents=[gce_subagent, gcs_subagent, finance_agent],
)
