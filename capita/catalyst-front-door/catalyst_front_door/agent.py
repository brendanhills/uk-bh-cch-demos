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

from google.adk.agents import Agent  

from .tools.tools import get_current_date, mcp_tools, search_tool, toolbox_tools


# Build tools list, filtering out empty/None values
tools = [get_current_date, search_tool, ]
if toolbox_tools:  # Only add if not empty list
    tools.extend(toolbox_tools)
if mcp_tools is not None:  # Only add if not None
    tools.append(mcp_tools)



input_capture_agent = Agent(
    name="input_capture_agent",
    model="gemini-2.5-flash",
    description="Input Capture via Natural Language: Help the user input their idea in natural language",
    instruction="""
        Users initiate a submission using chat or voice. The agent supports four primary request types:
            • Innovation ideas
        Confidential External - Data to be shared with caution.
            • Customer requests
            • Internal build requests
            • Pre-sales engagements
        """
    )

dynamic_context_agent = Agent(
    name="dynamic_context_agent",
    model="gemini-2.5-flash",
    description = "Dynamic Dialogue and Context Gathering: A guided conversation to understand the details of the idea",
    instruction = """
        The agent engages the user in a guided conversation to:
        • Clarify the intent of the request
        • Gather relevant context (e.g. business area, urgency, dependencies)
        • Estimate potential business impact and cost implications. 
        The agent asks probing questions to help:
        • Understanding the tools, stakeholders, clients and data sources
        • Flesh out and refine ideas through dynamic dialogue, acting as a virtual consultant to help users 
            explore possibilities, challenge assumptions, and strengthen the business        case before submission
        """
    )

intelligent_triage = Agent(
    name = "intelligent_triage",
    model = "gemini-3.0-pro",
    description = "Intelligent Triage: Classify the type of request and find duplicates",
    instruction = """
        Using AI-based classification, the agent:
        • Identifies the type of request
        • Detects duplicates or similar past submissions. Surfaces similar ideas and their original business users to the user,
          enabling them to build on existing work or connect directly with the idea owner.
        • Checks internal product lists for potential, pre-built solutions to the request. 
            It shouldask the user if an existing solution (“one we’ve built earlier”) fits their needs, 
            offering a link to the relevant product or submission for review.
        • Checks internal Catalyst Lab scope list. This enables the agent to know which Catalyst Lab member to assign to the request as it is dependent on scope of work.
        """
    )

automated_researcher = Agent(
    name = "automated_researcher",
    model="gemini-2.5-flash",
    description = "Automated Research: Research the idea",
    instruction = """
        The agent performs background analysis by:
            • Referencing previous Catalyst Lab submissions
            • Reviewing external market trends and comparable technologies
            • Estimating business impact and cost based on available data
        """
    )

pr_faq_generator = Agent(
    name = "pr_faq_generator",
    model = "gemini-3.0.pro",
    description = "PR/FAQ Style Summary Generation: Generate the output in a Press Release/FAQ style document",
    instruction = """
        Based on the gathered information, the agent:
        • Generates a concise, structured summary of the request with a detailed FAQ. 
            The summary should use data from the conversation plus contextual web search. 
            The FAQs should be relevant to the request and not the same every time.
        • Presents the summary to the user for review and refinement
        • Ensures clarity and alignment before final submission
        """
    )

refinement_loop = Agent(
    name = "refinement_loop",
    model = "gemini-3.0-pro",
    description= "Requestor Review and Refinement Loop: Refine the idea interactively with the user.",
    instruction = """
        The generated summary is generated in a PDF format and sent to the requestor through the chat interface for review. 
        The requestor can:
            1. Approve the summary if it accurately reflects their intent by stating that they approve in the chat.
            2. Suggest amendments if the summary is inaccurate or incomplete. They would do this in a response to the agent in the chat.
        If amendments are requested:
            • The agent initiates a second conversational interaction to understand what needs to be changed.
            • It asks targeted, contextual questions to refine its understanding.
            • The agent then re-runs the research and analysis steps to generate an updated summary.
            • This revised version is returned to the requestor for final approval.
    """
)


submission_creator = Agent(
    name = "submission_creator",
    model = "gemini-2.5-flash",
    description= "Structured Submission and Handoff: Create the document and store it.",
    instruction = """
        Once finalised:
        • The agent parses the submission into a structured format
        • Stores it in the Catalyst Lab SalesForce database with automated and consistent tagging of the request related to customer/contract, 
        business sector (CE, CPS, Group) or solution category (translation agent, knowledge agent, etc).
        • Enables visibility and traceability across the innovation lifecycle.
        • Notifies the Catalyst Lab that a new request has been added to the SalesForce database..
    """
)


root_agent = Agent(
    model="gemini-2.5-flash",
    name="catalyst_front_door",
    description="The Catalyst Lab “Front Door” AI Agent is a digital entry point for capturing, ideating and processing ideas across Capita. ",
    instruction="""


        Your job is to help the user develop an idea from a brief description to a Press Release/FAQ format document.  
        Go through the process in this order:
        1. Input Capture via Natural Language
        2. Dynamic Dialogue and Context Gathering
        3. Intelligent Triage
        4. Automated Research
        5. PR/FAQ Style Summary Generation
        6. Requestor Review and Refinement Loop
        7. Structured Submission and Handoff

""",
    tools=tools,
    sub_agents=[input_capture_agent, dynamic_context_agent, intelligent_triage, automated_researcher,pr_faq_generator, refinement_loop, submission_creator]
)