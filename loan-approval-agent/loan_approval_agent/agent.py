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

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.investigator.agent import investigator_agent
from .sub_agents.policy_expert.agent import policy_expert_agent
from .sub_agents.underwriter.agent import risk_analyst_agent

from .config import ORCHESTRATOR_MODEL

loan_manager = LlmAgent(
    name="loan_manager",
    model=ORCHESTRATOR_MODEL,
    description=(
        "Orchestrates the loan approval process by managing a team of expert sub-agents "
        "to investigate, review policy, and make a final decision."
    ),
    instruction=prompt.LOAN_MANAGER_PROMPT,
    output_key="final_decision",
    tools=[
        AgentTool(agent=investigator_agent),
        AgentTool(agent=policy_expert_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)

root_agent = loan_manager
