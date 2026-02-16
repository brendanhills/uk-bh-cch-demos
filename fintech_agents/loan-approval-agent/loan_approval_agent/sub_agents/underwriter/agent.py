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

"""Underwriter agent for making final loan decisions."""

from google.adk import Agent
from . import tools
from . import prompt

from ...config import UNDERWRITER_MODEL

risk_analyst_agent = Agent(
    model=UNDERWRITER_MODEL,
    name="risk_analyst_agent",
    instruction=prompt.RISK_ANALYST_PROMPT,
    output_key="final_decision_output",
    tools=[tools.record_decision, tools.escalate_app],
)
