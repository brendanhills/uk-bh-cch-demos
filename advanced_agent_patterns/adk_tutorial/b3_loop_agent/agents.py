from google.adk.tools import google_search, ToolContext
from google.adk.agents import Agent, LoopAgent, SequentialAgent
from dotenv import load_dotenv

load_dotenv()

# A tool to signal that the loop should terminate
COMPLETION_PHRASE = "The plan is feasible and meets all constraints."
def exit_loop(tool_context: ToolContext):
  """Call this function ONLY when the plan is approved, signaling the loop should end."""
  print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
  tool_context.actions.escalate = True
  return {}

# Agent 1: Proposes an initial plan
planner_agent = Agent(
    name="planner_agent", 
    model="gemini-flash-latest", 
    tools=[google_search],
    instruction="You are a trip planner. Based on the user's request, propose a single activity and a single restaurant. Output only the names, like: 'Activity: Exploratorium, Restaurant: La Mar'.",
    output_key="current_plan"
)

# Agent 2 (in loop): Critiques the plan
critic_agent = Agent(
    name="critic_agent", model="gemini-flash-latest", tools=[google_search],
    instruction=f"""You are a logistics expert. Your job is to critique a travel plan. The user has a strict constraint: total travel time must be short.
    Current Plan: {{current_plan}}
    Use your tools to check the travel time between the two locations.
    IF the travel time is over 45 minutes, provide a critique, like: 'This plan is inefficient. Find a restaurant closer to the activity.'
    ELSE, respond with the exact phrase: '{COMPLETION_PHRASE}'""",
    output_key="criticism"
)

# Agent 3 (in loop): Refines the plan
refiner_agent = Agent(
    name="refiner_agent", 
    model="gemini-flash-latest", 
    tools=[google_search],
    instruction=f"""You are a trip planner, refining a plan based on criticism.
    Original Request: {{session.query}}
    Critique: {{criticism}}
    IF the critique is '{COMPLETION_PHRASE}', you MUST respond with the exact phrase '{COMPLETION_PHRASE}'.
    ELSE, generate a NEW plan that addresses the critique. Output only the new plan names, like: 'Activity: de Young Museum, Restaurant: Nopa'.""",
    output_key="current_plan"
)

# Agent 4 (in loop): Exits the loop if the plan is good
exit_agent = Agent(
    name="exit_agent",
    model="gemini-flash-latest",
    tools=[exit_loop],
    instruction=f"""You are an exit controller.
    IF the input is '{COMPLETION_PHRASE}', you MUST call the 'exit_loop' tool.
    ELSE, do nothing."""
)

# ✨ The LoopAgent orchestrates the critique-refine cycle ✨
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[critic_agent, refiner_agent, exit_agent],
    max_iterations=3
)

# ✨ The SequentialAgent puts it all together ✨
iterative_planner_agent = SequentialAgent(
    name="iterative_planner_agent",
    sub_agents=[planner_agent, refinement_loop],
    description="A workflow that iteratively plans and refines a trip to meet constraints."
)

print("🤖 Agent team updated with an iterative LoopAgent workflow!")

root_agent = iterative_planner_agent