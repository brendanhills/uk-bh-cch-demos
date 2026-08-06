import logging
from typing import AsyncGenerator
import re

# Import ADK components
from google.adk.agents import LlmAgent, BaseAgent, ParallelAgent, SequentialAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import google_search
from typing_extensions import override
from dotenv import load_dotenv

load_dotenv()


# --- 1. Define the Custom Budget-Aware Planner Agent ---

class BudgetAwarePlannerAgent(BaseAgent):
    """A custom agent that plans a trip while tracking a budget."""
    model_config = {"arbitrary_types_allowed": True}

    # Declare the class attributes that will be used. This avoids the "no field" error.
    budget_parser_agent: LlmAgent
    activity_finder_agent: LlmAgent
    cost_estimator_agent: LlmAgent
    restaurant_finder_agent: LlmAgent

    def __init__(self, name: str):
        """Initializes the agent and all its required sub-agents."""
        
        # Define the specialist agents this coordinator will use.
        budget_parser_agent = LlmAgent(
            name="BudgetParserAgent", model="gemini-flash-latest",
            instruction="Analyze the user's text to find a budget. Extract only the numerical value. For example, if the user says '$100' or '150 dollars', output only the number '100' or '150'.",
            output_key="total_budget"
        )
        activity_finder_agent = LlmAgent(
            name="ActivityFinderAgent", model="gemini-flash-latest", tools=[google_search],
            instruction="Find a popular museum or tourist activity in or near Sunnyvale, CA. Output only its name.",
            output_key="found_activity"
        )
        cost_estimator_agent = LlmAgent(
            name="CostEstimatorAgent", model="gemini-flash-latest", tools=[google_search],
            instruction="The user wants to know the cost for one adult ticket for the following place: {item_name}. Search for the price and output ONLY the numerical value. For example, if a ticket is $25.99, output '25.99'. If it's free, output '0'.",
            output_key="estimated_cost"
        )
        restaurant_finder_agent = LlmAgent(
            name="RestaurantFinderAgent", model="gemini-flash-latest", tools=[google_search],
            instruction="Find a moderately priced, well-rated restaurant in or near Sunnyvale, CA that is not fast food. Output only its name.",
            output_key="found_restaurant"
        )

        # Pass the name and all sub-agents to the parent constructor.
        super().__init__(
            name=name,
            budget_parser_agent=budget_parser_agent,
            activity_finder_agent=activity_finder_agent,
            cost_estimator_agent=cost_estimator_agent,
            restaurant_finder_agent=restaurant_finder_agent,
            sub_agents=[budget_parser_agent, activity_finder_agent, cost_estimator_agent, restaurant_finder_agent] 
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Implements the custom orchestration logic for budget-aware planning."""
        
        # 1. Parse the initial budget from the user's query.
        async for event in self.budget_parser_agent.run_async(ctx):
            yield event
        
        try:
            total_budget = float(ctx.session.state.get("total_budget", 0))
        except (ValueError, TypeError):
            total_budget = 0.0

        if total_budget <= 0:
            failure_agent = LlmAgent(name="FailureAgent", model="gemini-flash-latest", instruction="Politely inform the user that a valid budget is needed to begin planning and end the conversation.")
            async for event in failure_agent.run_async(ctx):
                yield event
            return

        # Initialize state for the planning loop.
        running_cost = 0.0
        itinerary = []
        
        # --- Planning Loop ---
        
        # 2. Plan Activity
        async for event in self.activity_finder_agent.run_async(ctx):
            yield event
        activity_name = ctx.session.state.get("found_activity")
        ctx.session.state["item_name"] = activity_name # Prepare input for cost estimator
        
        async for event in self.cost_estimator_agent.run_async(ctx):
            yield event
        try:
            # Clean the LLM output to get a number
            cost_str = re.findall(r"[\d.]+", str(ctx.session.state.get("estimated_cost", "0")))[0]
            activity_cost = float(cost_str)
        except (ValueError, IndexError):
            activity_cost = 25.0 # Default cost if parsing fails

        # 3. Python Decision Gate for Activity
        if (running_cost + activity_cost) <= total_budget:
            running_cost += activity_cost
            itinerary.append({"item": activity_name, "cost": activity_cost})
            feedback_agent = LlmAgent(name="FeedbackAgent", model="gemini-flash-latest", instruction=f"Inform the user that '{activity_name}' has been added to the plan. The current total is ${running_cost:.2f} of the ${total_budget:.2f} budget.")
            async for event in feedback_agent.run_async(ctx):
                yield event
        
        # 4. Plan Restaurant
        async for event in self.restaurant_finder_agent.run_async(ctx):
            yield event
        restaurant_name = ctx.session.state.get("found_restaurant")
        # For restaurants, we'll use an estimated average cost instead of a ticket price.
        restaurant_cost = 35.0 # Assume an average meal cost
        
        # 5. Python Decision Gate for Restaurant
        if (running_cost + restaurant_cost) <= total_budget:
            running_cost += restaurant_cost
            itinerary.append({"item": restaurant_name, "cost": restaurant_cost})
        
        # 6. Final Summary
        itinerary_details = ""
        if not itinerary:
            itinerary_details = "No items could be added within the budget."
        else:
            for item in itinerary:
                itinerary_details += f"* {item['item']}: Estimated Cost ${item['cost']:.2f}\n"

        # 2. Use a strict template for the final prompt.
        summary_instruction = f"""
        You are a helpful assistant. Your task is to present the final trip plan to the user.
        Use the following template EXACTLY. Do not add any horizontal lines, extra formatting, or conversational text.

        **Your Budget-Friendly Trip Plan**

        Your total budget was ${total_budget:.2f}.

        **Final Itinerary:**
        {itinerary_details}
        **Total Estimated Cost: ${running_cost:.2f}**
        """
        summary_agent = LlmAgent(name="SummaryAgent", model="gemini-flash-latest", instruction=summary_instruction, output_key="final_response")
        async for event in summary_agent.run_async(ctx):
            yield event

# --- 2. Instantiate the Agent ---
root_agent = BudgetAwarePlannerAgent(name="BudgetAwarePlannerAgent")
print("🤖 Budget-Aware Planner Agent is ready.")