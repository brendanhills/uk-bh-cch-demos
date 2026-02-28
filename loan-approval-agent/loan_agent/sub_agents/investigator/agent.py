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

"""Investigator agent for gathering applicant data."""

from google.adk import Agent
from . import tools
from . import prompt

from ...config import INVESTIGATOR_MODEL, get_gen_config

investigator_agent = Agent(
    model=INVESTIGATOR_MODEL,
    generate_content_config=get_gen_config(is_pro=False),
    name="investigator_agent",
    instruction=prompt.INVESTIGATOR_PROMPT,
    output_key="investigation_report",
    tools=[
        tools.get_credit_report, 
        tools.verify_employment, 
        tools.check_fraud_risk, 
        tools.analyze_document,
        tools.calculate_dti,
        tools.check_data_consistency,
        tools.log_investigation_finding,
    ],
)
