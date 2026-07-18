import os
from google.adk import Agent
from google.adk.tools import FunctionTool

# --- Mock Geopolitical Data Tool ---
def query_geopolitical_data(region: str, topic: str) -> str:
    """Queries mock geopolitical insights for a region and topic."""
    data = {
        "APAC": {
            "trade": "Tensions rising in trade routes due to new tariffs in the South China Sea.",
            "stability": "Moderate stability; elections in key partner countries pending."
        },
        "EMEA": {
            "energy": "Significant shift towards renewable energy investments in Northern Europe.",
            "conflict": "Continued volatility in border regions affecting supply chains."
        }
    }
    return data.get(region, {}).get(topic, f"No specific data found for {region} - {topic}.")

query_geo_tool = FunctionTool(func=query_geopolitical_data)

# --- Geopolitical Agent ---
geo_agent = Agent(
    name="geo_researcher",
    model="gemini-2.0-flash-001",
    instruction="""You are a Geopolitical Research Agent. 
    You have access to specialized data sources via tools.
    Provide nuanced insights based on the region and topic requested by the user.""",
    tools=[query_geo_tool]
)
