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

from google.adk.agents import LlmAgent 

from .tools.tools import mcp_tools, search_tool, toolbox_tools


# Build tools list, filtering out empty/None values
tools = [search_tool, ]
if toolbox_tools:  # Only add if not empty list
    tools.extend(toolbox_tools) # type: ignore
if mcp_tools is not None:  # Only add if not None
    tools.append(mcp_tools) # type: ignore



input_capture_agent = LlmAgent(
    name="input_capture_agent",
    model="gemini-2.5-pro",
    instruction="""
        You are an innovation partner. Your role is to help the user capture and develop their initial idea.
        Start by having a friendly conversation to understand their idea. Avoid a long list of questions.
        Guide them to describe the core concept. Once you have a high level understanding, generate a concise and descriptive title (no more than 10 words) from their description.
        You'll also need the submitter's email address.
        Once you have the generated title, the description, and the submitter's email, use the `create_initial_idea` tool to create a record of the idea.
        Remember to keep the conversation natural and encouraging. You are here to help them plant the seed of a great idea.
        Store the returned idea ID for other agents to use.
        Users initiate a submission using chat or voice. The agent supports four primary request types:
            • Innovation ideas
            • Customer requests
            • Internal build requests
            • Pre-sales engagements

        Once you have stored the idea in the ideas table, call `transfer_to_agent` to pass the interaction to `dynamic_context_agent` to develop the idea further.
        """,
    tools=toolbox_tools # type: ignore
    )

intelligent_triage = LlmAgent(
    name = "intelligent_triage",
    model = "gemini-2.5-flash",
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

automated_researcher = LlmAgent(
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

dynamic_context_agent = LlmAgent(
    name="dynamic_context_agent",
    model="gemini-2.5-flash",
    description = "Dynamic Dialogue and Context Gathering: A guided conversation to understand the details of the idea",
    instruction = """
        You are an innovation partner, continuing the conversation from the initial idea capture. You will be given the ID of the idea.
        Your goal is to help the user develop their idea further. Instead of a rapid-fire Q&A, have a collaborative conversation.
        Encourage the user to think about:
        - **Impact:** Who benefits from this idea? What would be the positive change?
        - **Gaps & Risks:** What are the unknowns? What could go wrong?
        - **Iterative Development:** What would be a simple first version (MVP)? How can we build on it over time?

        Your role is to be a supportive collaborator, helping the user to think more deeply about their idea and its potential.

        As you discuss and uncover new details, you should use the specific update tools available to you to enrich the idea's record in the database.
        For example, if you learn about the return on investment, use the `update-idea-roi` tool. If you get a new description, use the `update-idea-description` tool.
        Call these tools as soon as you have new information to save progress. You must provide the idea ID and the new value for the field you are updating.
        Your role is to be a supportive collaborator, helping the user to think more deeply about their idea and its potential.
        """,
    tools=toolbox_tools, # type: ignore
  )

pr_faq_generator = LlmAgent(
    name = "pr_faq_generator",
    model = "gemini-2.5-flash",
    description = "PR/FAQ Style Summary Generation: Generate the output in a Press Release/FAQ style document",
    instruction = """
        Based on the gathered information, the agent:
        • Generates a concise, structured summary of the request with a detailed FAQ in JSON format.
            The summary should use data from the conversation plus contextual web search.
            The FAQs should be relevant to the request and not the same every time.
        • Presents the summary to the user for review and refinement.
        • Once the user approves, you must use the update-idea tool to store the generated JSON document in the pr_faq_doc column for the given idea ID.
        • Ensures clarity and alignment before final submission.
        """,
    tools=toolbox_tools # type: ignore
)

refinement_loop = LlmAgent(
    name = "refinement_loop",
    model = "gemini-2.5-flash",
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
    """,
    tools=toolbox_tools # type: ignore
)


submission_creator = LlmAgent(
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
    """,
    tools=toolbox_tools # type: ignore
)


list_ideas_agent = LlmAgent(
    name="list_ideas_agent",
    model="gemini-2.5-flash",
    description="Lists ideas in the database.",
    instruction="""
        Your job is to list ideas from the database. You can use the search-ideas tool to do this.
        When a user asks to list ideas, you can ask for a query to search for, or if they don't provide one, you can search for all ideas by passing an empty query.
        """,
    tools=toolbox_tools # type: ignore
)


root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="catalyst_front_door",
    description="The Catalyst Lab “Front Door” AI Agent is a digital entry point for capturing, ideating and processing ideas across Capita. ",
    instruction="""

        Your job is to help the user develop an idea from a brief description to a Press Release/FAQ format document.  
        Go through the process in this order:
        1. Input Capture via Natural Language. Call input_capture_agent to have the initial conversation with the user and create a new idea record.  Pass the record ID to each subsequent agent
        2. Dynamic Dialogue and Context Gathering. Hand off to the following sub-agents 
            2.1. Intelligent Triage
            2.2. Automated Research
        5. PR/FAQ Style Summary Generation
        6. Requestor Review and Refinement Loop
        7. Structured Submission and Handoff

        If the user asks to list ideas, use the list-ideas_agent.
""",
    sub_agents=[input_capture_agent, dynamic_context_agent, pr_faq_generator]
)