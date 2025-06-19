from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, Agent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import Content, Part
import asyncio
from .sub_agents.incorrect_weight import incorrect_weight_tool_wrapper
from .sub_agents.incorrect_format import incorrect_format_tool_wrapper
from .sub_agents.data.load_csv import load_parcel_data
import json
from google.adk.tools import load_memory

APP_NAME = "parcel_app"
USER_ID = "parcel_user"
MODEL = "gemini-2.0-flash"

session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
runner = Runner(
    agent=None,  # We'll set the agent later
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)

# Caching logic
global cached_format_data
cached_format_data = None

# global cached_weight_data
# cached_weight_data = None


def load_and_process_format_data(_: str = "") -> str:
    global cached_format_data
    if cached_format_data is not None:
        return cached_format_data
    parcel_data_json = load_parcel_data()
    if "error" in parcel_data_json:
        return parcel_data_json
    data = json.loads(parcel_data_json)
    cached_format_data = incorrect_format_tool_wrapper(json.dumps(data))
    return cached_format_data


data_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="data_analysis_agent",
    description="provide data to the appropriate agents.",
    instruction="You are the data Agent. your task is to provide data analysis based on question if the question is about format or weight Your task is to pass the question to 'incorrect_format_agent' and 'incorrect_weight_agent'. ",
    tools=[load_and_process_format_data],
    )

greeting_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="greeting_agent",
    description="Handles simple greetings.",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user."
                "For general greetings (hi, hello, etc.): Respond with a friendly greeting and brief introduction of your capabilities",

)


incorrect_format_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="incorrect_format_agent",
    description="Answers user questions about incorrect format based on tolerance.",
    instruction="""
    You are an agent tasked with determining if a parcel has incorrect format based on pre-calculated flags.

    **IMPORTANT RULES**:
    - Only respond to questions specifically about these keywords: {IncorrectFormatOutOfTolerance, FORMAT, FORMAT OUT OF TOLERANCE, INCORRECT FORMAT, FORMAT NON COMPLIANT, FORMAT SURCHARGE, HEIGHT, LENGTH, WIDTH}
    - Utilize the data obtained from 'data_agent' and use it for all queries
    - If IncorrectFormatOutOfTolerance = 1, then format is out of tolerance and it is non-compliant, so surcharge the customer
   
    **IMPORTANT CHECKLIST**:
    Check the data before you output - verify total data which you have access to and validate for any missing data
    Check "IncorrectFormatOutOfTolerance" - count how many are 1 and how many are 0, validate and output the data accordingly
    Output only the columns which the user requests
    Add a separate column for "Surcharge Reason" and provide reason for surcharge in your own words
    
    YOUR TASKS:
    Use the 'load_and_process_format_data' tool to get format analysis data
    Load the data_agent only ONCE and use it for all further queries
    Apply surcharge logic: If IncorrectFormatOutOfTolerance = 1, then it is non-compliant and surcharge the customer
    For records where IncorrectFormatOutOfTolerance = 1, add a separate "Surcharge Reason" column with explanation in your own words
    Provide detailed analysis based on the data in tabular format
    Add serial number column at the beginning of all output tables
   
    
    OUTPUT FORMAT:
    Present all results in tabular format
    Include serial numbers starting from 1
    Include requested columns plus "Surcharge Reason" column where applicable
    Provide summary statistics of compliant vs non-compliant parcels
    
""",
    tools=[load_and_process_format_data],
    output_key="incorrect_format_result")

incorrect_weight_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="incorrect_weight_agent",
    description="Answers user questions about weight of the parcel or package.",
    instruction="""
    You are an agent tasked with determining if a parcel has incorrect weight based on pre-calculated flags.
    
    **IMPORTANT RULES**:
    
    Utilize the data obtained from 'data_agent' and use it for all queries
     - Only respond to questions specifically about these keywords: {IncorrectFormatDueToWeightOutOfTolerance, INCORRECT WEIGHT, WEIGHT OUT OF TOLERANCE, WEIGHT NON COMPLIANT, WEIGHT SURCHARGE, WEIGHT TOLERANCE}
    If IncorrectFormatDueToWeightOutOfTolerance = 1, then weight is out of tolerance and it is non-compliant, so surcharge the customer
    
    **IMPORTANT CHECKLIST**:
    
    Check the data before you output - verify total data which you have access to and validate for any missing data
    Check "IncorrectFormatDueToWeightOutOfTolerance" - count how many are 1 and how many are 0, validate and output the data accordingly
    Output only the columns which the user requests
    Add a separate column for "Surcharge Reason" and provide reason for surcharge in your own words
    
    YOUR TASKS:
    Use the 'data_agent' tool to get weight analysis data
    Load the 'data_agent' only ONCE and use it for all further queries
    Apply surcharge logic: If IncorrectFormatDueToWeightOutOfTolerance = 1, then it is non-compliant and surcharge the customer
    For records where IncorrectFormatDueToWeightOutOfTolerance = 1, add a separate "Surcharge Reason" column with explanation in your own words
    Provide detailed analysis based on the data in tabular format
    Add serial number column at the beginning of all output tables
    Only process queries related to the specified weight-related keywords
    
    OUTPUT FORMAT:
    
    Present all results in tabular format
    Include serial numbers starting from 1
    Include requested columns plus "Surcharge Reason" column where applicable
    Provide summary statistics of compliant vs non-compliant parcels
""",
    tools=[load_and_process_format_data],
    output_key="incorrect_weight_result"
)

main_orchestrator = LlmAgent(
    model=MODEL,
    name="main_orchestrator",
    instruction="""
    
    For general greetings (hi, hello, etc.): Respond with a friendly greeting and brief introduction of your capabilities.
        You are a parcel analysis assistant designed to analyze parcel compliance and surcharge requirements.
        
        YOU HAVE SPECIALIZED TOOLS:
        
        1) 'greeting_agent': - For general greetings (hi, hello, etc.): Respond with a friendly greeting and brief introduction of your capabilities.
            - if the user query is about format transfer it to 'incorrect_format_agent'
            - if the user query is about weight transfer it to 'incorrect_weight_agent'
        
        2) 'data_agent': Read the data and pass the data to appropriate agent.
        3) 'incorrect_format_agent': Analyzes format compliance
            - Utilizes data from 'load_and_process_format_data'
            - Only respond to questions specifically about these keywords: {IncorrectFormatOutOfTolerance, FORMAT, FORMAT OUT OF TOLERANCE, INCORRECT FORMAT, FORMAT NON COMPLIANT, FORMAT SURCHARGE, HEIGHT, LENGTH, WIDTH}
            - Utilizes data from 'load_and_process_format_data' give result as per 'incorrect_format_agent'
        4) 'incorrect_weight_agent': Analyzes weight compliance
            - Only respond to questions specifically about these keywords: {IncorrectFormatDueToWeightOutOfTolerance, INCORRECT WEIGHT, WEIGHT OUT OF TOLERANCE, WEIGHT NON COMPLIANT, WEIGHT SURCHARGE, WEIGHT TOLERANCE}
            - Utilizes data from 'load_and_process_format_data' and give results as per 'incorrect_weight_agent'
        
        WORKFLOW:
    
        - Analyze user query intent
        - Determine which tool(s) to use
        - Execute appropriate analysis
        - Present results in structured format
        - Include actionable insights about compliance and surcharges
    """,
    tools= [AgentTool(agent= greeting_agent),
            AgentTool(agent= data_agent),
            AgentTool(agent = incorrect_format_agent),
            AgentTool(agent = incorrect_weight_agent)]
)

summary_agent = LlmAgent(
    model=MODEL,
    name="summary_agent",
    description = "Provides checker and provides the summary",
    instruction=""" 1) if the user greets 'hello', 'hi' etc provide the 'greeting_agent' response' from 'main_orchestrator'.
                
                2) if the query is in this keywords: {IncorrectFormatOutOfTolerance, FORMAT, FORMAT OUT OF TOLERANCE, INCORRECT FORMAT, FORMAT NON COMPLIANT, FORMAT SURCHARGE, HEIGHT, LENGTH, WIDTH}, use 'incorrect_format_agent' from  'main_orchestrator' and data and also give the summary of results.
                3) if the query is in this keywords: {IncorrectFormatDueToWeightOutOfTolerance, INCORRECT WEIGHT, WEIGHT OUT OF TOLERANCE, WEIGHT NON COMPLIANT, WEIGHT SURCHARGE, WEIGHT TOLERANCE}, use 'incorrect_format_agent' from  'main_orchestrator' and give data and also the summary of results. 
                """,
    tools= [AgentTool(agent=main_orchestrator)])

root_agent = summary_agent

recall_agent = LlmAgent(
    model=MODEL,
    name="RecallAgent",
    instruction="Use the 'load_memory' tool to recall previous analysis results if user asks for them.",
    tools=[load_memory],
)


# --- Function to run the agent with session handling ---
# Function to process queries
async def process_parcel_query():
    """Process parcel analysis queries."""
    runner.agent = root_agent
    session_id = "session_info"

    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id = session_id
    )
    user_input = Content(parts=[Part(text="Check the parcel for incorrect weight and format.")], role="user")

    print("\n--- Running Parcel Analysis ---")
    final_response = "(No response yet)"
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_input):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            print("Final Response:\n", final_response)

    print("\n--- Adding to Memory ---")
    completed_session = await session_service.get_session(APP_NAME, USER_ID, session_id)
    await memory_service.add_session_to_memory(completed_session)


async def run_memory_recall():
    runner.agent = recall_agent  # Use memory agent

    session_id = "parcel_memory_recall_session"
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)

    user_input = Content(parts=[Part(text="What did the previous analysis say?")], role="user")

    print("\n--- Running Memory Recall ---")
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=user_input):
        if event.is_final_response() and event.content and event.content.parts:
            print("Memory Recall Response:\n", event.content.parts[0].text)
            break


if __name__ == "__main__":
    asyncio.run(process_parcel_query())  # Run analysis
    asyncio.run(run_memory_recall())    # Recall results (optional)
agent = root_agent