# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Loan Manager: orchestrates the loan approval process."""

from google.adk.apps import App as AdkApp
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from loan_agent import prompt
from loan_agent.sub_agents.investigator.agent import investigator_agent
from loan_agent.sub_agents.policy_expert.agent import policy_expert_agent
from loan_agent.sub_agents.underwriter.agent import underwriter_agent


from loan_agent.tools.intake import register_application
from loan_agent.config import ORCHESTRATOR_MODEL, get_gen_config

from google.genai import types

async def greet_user_callback(callback_context):
    """Greets the user at the start of the conversation."""
    # Check if there are any events from the agent in the session
    # (author='user' events are the incoming message that triggered this)
    history = callback_context._invocation_context.session.events
    agent_events = [e for e in history if e.author != "user"]
    
    if not agent_events:
        # This is the first time the agent is speaking
        return types.Content(
            role="assistant",
            parts=[types.Part.from_text(text="Welcome to FastLoan! I'm your automated loan assistant. To get started, please provide your Name, Government ID, Employer, and the Loan Amount you are requesting.")]
        )
    return None

loan_manager = LlmAgent(
    name="loan_manager",
    model=ORCHESTRATOR_MODEL,
    generate_content_config=get_gen_config(is_pro=False),
    before_agent_callback=greet_user_callback,
    description=(
        "Orchestrates the loan approval process by managing a team of expert sub-agents "
        "to investigate, review policy, and make a final decision."
    ),
    instruction=prompt.LOAN_MANAGER_PROMPT,
    output_key="final_decision",
    sub_agents=[],
    tools=[
        register_application,
        AgentTool(agent=investigator_agent),
        AgentTool(agent=policy_expert_agent),
        AgentTool(agent=underwriter_agent),
    ],
)

root_agent = loan_manager

app = AdkApp(
    name="loan_agent",
    root_agent=root_agent,
)
