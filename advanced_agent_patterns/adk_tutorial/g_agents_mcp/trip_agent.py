# agents/trip_agent.py
from google.adk.agents import Agent
from toolbox_core import ToolboxSyncClient
from dotenv import load_dotenv

# Import our new memory tools

load_dotenv()

# Connect to the MCP Toolbox server running on port 7001
# Note the different port number from the previous lab.
toolbox = ToolboxSyncClient("http://127.0.0.1:7001")

# Load the toolset we defined in trip_tools.yaml
tools = toolbox.load_toolset('trip-planner-tools')

# Define the Trip Agent
root_agent = Agent(
    model='gemini-flash-latest',
    name='trip_planner_agent',
    description='Agent that helps users plan trips by finding destinations.',
    instruction="""
    You are a friendly and helpful trip planning assistant.
    Your goal is to help users find interesting destinations based on their requests.
    You have access to a database of destinations with the following tools:

    - `find_destinations_by_type`: Use this when the user asks for a specific kind
      of place, like a "museum" or "park" in a specific city.
      Requires `city` and `type` as parameters.

    - `find_top_rated_in_city`: Use this when the user asks for the "best" or
      "top-rated" things to do in a city.
      Requires a `city` parameter.

    - `find_affordable_options`: Use this when the user mentions a budget or asks
      for "cheap" or "free" options.
      Requires a `city` and a `max_cost`.

    Based on the user's question, choose the most appropriate tool, call it with
    the correct parameters, and present the results in a clear, easy-to-read format.
    """,
    tools=tools,
)

print("🤖 Trip Planner Agent is ready.")