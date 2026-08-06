import logging
from typing import AsyncGenerator, Dict, Any
import os

# Import ADK components
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import ToolContext, google_search
from google.adk.tools.agent_tool import AgentTool
from typing_extensions import override
from dotenv import load_dotenv

# Import our new memory tools

load_dotenv()


# --- 1. Define the Session-based Memory Tools ---
def save_user_preferences(tool_context: ToolContext, new_preferences: Dict[str, Any]) -> str:
    """
    Saves or updates user preferences in the persistent session storage.
    It merges new preferences with any existing ones.

    Args:
        new_preferences: A dictionary of new preferences to save.
                         Example: {"cuisine": "Italian", "interests": ["modern art"]}
    """
    # --- FIX: Read from tool_context.state, which is the correct path in this library version ---
    current_preferences = tool_context.state.get('user_preferences') or {}
    current_preferences.update(new_preferences)

    # --- FIX: Write directly to tool_context.state. The ADK framework will persist this change. ---
    tool_context.state['user_preferences'] = current_preferences
    
    return f"Preferences updated successfully: {new_preferences}"

def recall_user_preferences(tool_context: ToolContext) -> Dict[str, Any]:
    """Recalls all saved preferences for the current user from the session."""
    # --- FIX: Read from tool_context.state, the correct path in this library version ---
    preferences = tool_context.state.get('user_preferences')
    
    if preferences:
        return preferences
    else:
        return {"message": "No preferences found for this user."}


# --- 2. Define the Specialist "Tool" Agent ---
planner_tool_agent = LlmAgent(
    name="PlannerToolAgent",
    model="gemini-flash-latest",
    description="A specialist that finds activities and restaurants based on a user's request and preferences.",
    instruction="""
    You are a planning assistant. Based on the user's request and their provided preferences, find one activity and one restaurant in Sunnyvale.
    Output the plan as a simple JSON object.
    Example: {"activity": "The Tech Interactive", "restaurant": "Il Postale"}
    """,
    tools=[google_search]
)

# --- 3. Define the Main Coordinator Agent ---
root_agent = LlmAgent(
    name="MemoryCoordinatorAgent",
    model="gemini-flash-latest",
    instruction="""
    You are a highly intelligent, personalized trip planner with a persistent memory.
    1. RECALL FIRST: At the absolute beginning of the conversation, your first action MUST be to call the `recall_user_preferences` tool.
    2. PERSONALIZE & PLAN: Use the recalled preferences to enrich the user's current request. Call the `PlannerToolAgent` with the combined request.
    3. PRESENT & LEARN: Present the plan. Then, ask for feedback and if there are any new preferences you should save.
    4. SAVE LAST: If the user provides a new preference, your final action MUST be to call the `save_user_preferences` tool.
    """,
    tools=[
        recall_user_preferences,
        save_user_preferences,
        AgentTool(agent=planner_tool_agent)
    ]
)

print("🤖 Memory Coordinator Agent (with ADK Session Service) is ready.")