from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.agents import Agent, SequentialAgent
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from b3_loop_agent.agents import iterative_planner_agent
from b2_parallel_agent.agents import parallel_planner_agent
from c_custom_agent.agents import root_agent as custom_agent
from dotenv import load_dotenv

load_dotenv()

# --- Agent Definitions for our Specialist Team (Refactored for Sequential Workflow) ---
day_trip_agent = Agent(
    name="day_trip_agent",
    model="gemini-flash-latest",
    description="Agent specialized in generating spontaneous full-day itineraries based on mood, interests, and budget.",
    instruction="""
    You are the "Spontaneous Day Trip" Generator 🚗 - a specialized AI assistant that creates engaging full-day itineraries.

    Your Mission:
    Transform a simple mood or interest into a complete day-trip adventure with real-time details, while respecting a budget.

    Guidelines:
    1. **Budget-Aware**: Pay close attention to budget hints like 'cheap', 'affordable', or 'splurge'. Use Google Search to find activities (free museums, parks, paid attractions) that match the user's budget.
    2. **Full-Day Structure**: Create morning, afternoon, and evening activities.
    3. **Real-Time Focus**: Search for current operating hours and special events.
    4. **Mood Matching**: Align suggestions with the requested mood (adventurous, relaxing, artsy, etc.).

    RETURN itinerary in MARKDOWN FORMAT with clear time blocks and specific venue names.
    """,
    tools=[google_search]
)

# ✨ CHANGE 1: We tell foodie_agent to save its output to the shared state.
# Note the new `output_key` and the more specific instruction.
foodie_agent = Agent(
    name="foodie_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="""You are an expert food critic. Your goal is to find the best restaurant based on a user's request.

    When you recommend a place, you must output *only* the name of the establishment and nothing else.
    For example, if the best sushi is at 'Jin Sho', you should output only: Jin Sho
    """,
    output_key="destination"  # ADK will save the agent's final response to state['destination']
)

# ✨ CHANGE 2: We tell transportation_agent to read from the shared state.
# The `{destination}` placeholder is automatically filled by the ADK from the state.
transportation_agent = Agent(
    name="transportation_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="""You are a navigation assistant. Given a destination, provide clear directions.
    The user wants to go to: {destination}.

    Analyze the user's full original query to find their starting point.
    Then, provide clear directions from that starting point to {destination}.
    """,
)

# ✨ CHANGE 3: Define the SequentialAgent to manage the workflow.
# This agent will run foodie_agent, then transportation_agent, in that exact order.
find_and_navigate_agent = SequentialAgent(
    name="find_and_navigate_agent",
    sub_agents=[foodie_agent, transportation_agent],
    description="A workflow that first finds a location and then provides directions to it."
)

weekend_guide_agent = Agent(
    name="weekend_guide_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="You are a local events guide. Your task is to find interesting events, concerts, festivals, and activities happening on a specific weekend."
)


day_trip_workflow = SequentialAgent(
    name="day_trip_workflow",
    sub_agents=[day_trip_agent],
    description="A workflow that plans a full day itinerary."
)

weekend_guide_workflow = SequentialAgent(
    name="weekend_guide_workflow",
    sub_agents=[weekend_guide_agent],
    description="A workflow that finds weekend events."
)


# --- The Brain of the Operation: The Router Agent ---
# This is the new instruction block for your router_agent
new_router_instruction = """
You are a master coordinator for a team of specialist AI travel agents.
Your primary job is to analyze the user's request and delegate it to the single most appropriate agent or workflow from your team.
You must invoke the chosen agent and return its complete, final response to the user.

--- Decision-Making Process ---
Think step-by-step to make the most accurate choice. Follow this priority order:

1.  **Is there a BUDGET?** If the user mentions money, cost, or a price (e.g., "$", "dollars", "cheap", "under 100"), you MUST use the `budget_planner_agent`. This is your top priority.
2.  **Is there a specific CONSTRAINT that requires iteration?** If the user asks for a plan that must be optimized (e.g., "shortest travel time", "most efficient", "critique this plan"), you MUST use the `iterative_planner_agent`.
3.  **Are there MULTIPLE, DIVERSE requests at once?** If the user asks for several different types of things in one go (e.g., "Find a museum, a concert, and a taco place"), you MUST use the `parallel_planner_agent` for efficiency.
4.  **If none of the above, use a general planner.** Fall back to the simpler agents for standard requests.

--- Agent Capabilities ---

- `budget_planner_agent`: A specialist that plans a full trip while staying under a specific monetary budget provided by the user. Contains custom logic for cost calculation.
- `iterative_planner_agent`: A workflow that first creates a plan and then iteratively refines it based on a specific constraint (like travel time) until the plan is optimal.
- `parallel_planner_agent`: A high-speed research assistant that finds multiple different things (e.g., a museum, a concert, a restaurant) at the same time and then summarizes the results.
- `day_trip_workflow`: A simple planner for a single-day itinerary when no special constraints or budget are mentioned.
- `weekend_guide_workflow`: A simple guide for finding specific, time-based EVENTS (like concerts or festivals) happening on a weekend.
- `find_and_navigate_agent`: A simple tool to find a single location and get directions to it.

--- Examples ---
- User: "Plan a day in Sunnyvale for me for under $75." -> `budget_planner_agent`
- User: "Plan a trip to SF, but make sure the activities are close to each other to minimize travel." -> `iterative_planner_agent`
- User: "For my trip, find me a good museum, a rock concert, and a place for ramen." -> `parallel_planner_agent`
- User: "What are some fun things I can do today?" -> `day_trip_workflow`

Now, analyze the user's request and orchestrate the correct agent.
"""

# We update the router to know about our new, powerful SequentialAgent.
router_agent = Agent(
    name="router_agent",
    model="gemini-flash-latest",
    instruction=new_router_instruction,
    sub_agents=[weekend_guide_workflow, day_trip_workflow, find_and_navigate_agent, iterative_planner_agent,  custom_agent],
)


print("🤖 Agent team assembled with a SequentialAgent workflow!")
root_agent = router_agent