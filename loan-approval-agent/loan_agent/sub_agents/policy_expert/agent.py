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

"""Policy Expert agent for evaluating loan applications."""

from google.adk import Agent
from . import tools
from . import prompt

from ...config import POLICY_EXPERT_MODEL, get_gen_config

policy_expert_agent = Agent(
    model=POLICY_EXPERT_MODEL,
    generate_content_config=get_gen_config(is_pro=True),
    name="policy_expert_agent",
    instruction=prompt.POLICY_EXPERT_PROMPT,
    output_key="policy_assessment",
    tools=[tools.consult_policy_docs],
)
