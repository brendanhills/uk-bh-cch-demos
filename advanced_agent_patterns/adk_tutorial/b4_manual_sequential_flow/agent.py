from google.adk.agents import Agent
from google.adk.tools import google_search
from dotenv import load_dotenv

load_dotenv()

# --- Agent Definitions for our Specialist Team ---
# --- Agent Definition ---

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
    """""
)

foodie_agent = Agent(
    name="foodie_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="You are an expert food critic. Your goal is to find the absolute best food, restaurants, or culinary experiences based on a user's request. When you recommend a place, state its name clearly. For example: 'The best sushi is at **Jin Sho**.'"
)

weekend_guide_agent = Agent(
    name="weekend_guide_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="You are a local events guide. Your task is to find interesting events, concerts, festivals, and activities happening on a specific weekend."
)

transportation_agent = Agent(
    name="transportation_agent",
    model="gemini-flash-latest",
    tools=[google_search],
    instruction="You are a navigation assistant. Given a starting point and a destination, provide clear directions on how to get from the start to the end."
)

# --- The Brain of the Operation: The Router Agent ---
# We update the router's instructions to know about the new 'combo' task.
router_agent = Agent(
    name="router_agent",
    model="gemini-flash-latest",
    instruction="""
    You are a request router. Your job is to analyze a user's query and decide which of the following agents or workflows is best suited to handle it.
    Do not answer the query yourself, only return the name of the most appropriate choice.

    Available Options:
    - 'foodie_agent': For queries *only* about food, restaurants, or eating.
    - 'weekend_guide_agent': For queries about events, concerts, or activities happening on a specific timeframe like a weekend.
    - 'day_trip_agent': A general planner for any other day trip requests.
    - 'find_and_navigate_combo': Use this for complex queries that ask to *first find a place* and *then get directions* to it.

    Only return the single, most appropriate option's name and nothing else.
    """""
)

# We'll create a dictionary of all our individual worker agents
worker_agents = {
    "day_trip_agent": day_trip_agent,
    "foodie_agent": foodie_agent,
    "weekend_guide_agent": weekend_guide_agent,
    "transportation_agent": transportation_agent, # Add the new agent!
}

print("🤖 Agent team assembled for sequential workflows!")