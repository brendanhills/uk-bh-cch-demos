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
# add docstring to this module

import logging
import os

from google.adk.agents import Agent
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from toolbox_core import ToolboxSyncClient

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


# ----- Example of a Built-in Tool -----
google_search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="""
    You're a specialist in Google Search.
    """,
    tools=[google_search],
)

google_search_tool = AgentTool(google_search_agent)

search_service_catalog = Agent(
    model="gemini-2.5-flash",
    name="search_service_catalog",
    instruction="""
    You are a tool to search the company's internal service catalog and list of available software.
    However, this search has not been implemented yet and you should return a polite message to the user saying that this service has not been implemented yet.
    """,
)

service_catalog_tool = AgentTool(search_service_catalog)

agent_tools = [google_search_tool, service_catalog_tool]


# ----- Example of a Google Cloud Tool (MCP Toolbox for Databases) -----
TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL", "http://127.0.0.1:5000")

# Initialize Toolbox client and load tools
# If the toolbox server is not available (e.g., in CI), set to empty list
try:
    toolbox = ToolboxSyncClient(TOOLBOX_URL)
    toolbox_tools = toolbox.load_toolset("ideas-toolset")
    logger.info(f"Loaded {len(toolbox_tools)} tools from Toolbox at {TOOLBOX_URL}")

except Exception:
    # Toolbox server not available, set to empty list
    logger.warning(f"Toolbox server at {TOOLBOX_URL} not available, using empty list of tools")
    toolbox_tools = []


# ----- Example of an MCP Tool (streamable-http) -----
# If GitHub token is not available (e.g., in CI), set to None
try:
    mcp_tools = [
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": "Bearer " + os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
                },
            ),
            # Read only tools
            tool_filter=[
                "search_ideas",
                "list_ideas",
                "get_idea",
            ]
        )
 ]
except Exception:
    # GitHub MCP server not available or token missing
    mcp_tools = None
