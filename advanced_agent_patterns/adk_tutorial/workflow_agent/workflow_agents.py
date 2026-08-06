from google.adk.tools import google_search
from google.adk.agents import Agent
from google.adk import Workflow
from google.adk.workflow import JoinNode
from dotenv import load_dotenv

load_dotenv()

# Specialist Agent 1
museum_finder_agent = Agent(
    name="museum_finder_agent", model="gemini-flash-latest", tools=[google_search],
    instruction="You are a museum expert. Find the best museum based on the user's query. Output only the museum's name. If no suitable museum is found, output: 'No museum found.'",
)

# Specialist Agent 2
concert_finder_agent = Agent(
    name="concert_finder_agent", model="gemini-flash-latest", tools=[google_search],
    instruction="You are an events guide. Find a concert based on the user's query. Output only the concert name and artist. If no suitable concert is found, output: 'No concert found.'",
)

# Specialist Agent 3
restaurant_finder_agent = Agent(
    name="restaurant_finder_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="""You are an expert food critic. Your goal is to find the best restaurant based on a user's request.

    When you recommend a place, you must output *only* the name of the establishment.
    For example, if the best sushi is at 'Jin Sho', you should output only: Jin Sho

    If you cannot find a suitable restaurant, output: 'No restaurant found.'
    """,
)

# Agent to synthesize the parallel results
synthesis_agent = Agent(
    name="synthesis_agent", model="gemini-flash-latest",
    instruction="""You are a helpful assistant. Review the provided conversation context and research results. 
    Combine the findings (museums, concerts, restaurants) into a clear, bulleted list for the user. If any category is missing from the context, simply skip it.
    """
)

join_node = JoinNode(name="join_for_results")

# ✨ The Workflow runs the parallel search, then the synthesis ✨
workflow_planner_agent = Workflow(
    name="parallel_planner_agent",
    edges=[(
        # Fan-Out: Trigger all three simultaneously
            "START",
            (museum_finder_agent, concert_finder_agent, restaurant_finder_agent),
            join_node,
            synthesis_agent,
        ),
    ]
)

root_agent = workflow_planner_agent
print("🤖 Agent team supercharged with a Workflow!")