from google.adk.agents.llm_agent import LlmAgent
from .tools import apihub_toolset, connector_tool, integration_tool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.tools.apihub_tool.clients.secret_client import SecretManagerClient

import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)


# ----------------------- Python Code Tool ------------------------------------

def get_ce(city: str) -> dict:
    """Retrieves the current CE aka customer engineer present now in a specified city.
    Args:
        city (str): The name of the city for which to retrieve the CE.
    Returns:
        dict: status and result or error msg.
    """
    # Best Practice: Log tool execution for easier debugging
    print(f"--- Tool: get_ce called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "") # Basic input normalization
 
    # Mock weather data for simplicity (matching Step 1 structure)
    mock_pm_db = {
        "dubai": {"status": "success", "report": "Mehdi and Ayman (BAP Solar Panel CEs) are based in Dubai."},
        "london": {"status": "success", "report": "Harish, Nigel, Nicola, Omid and Saravana (BAP Solar Panel CEs & TSC) are based in London."},
        "berlin": {"status": "success", "report": "Tyler (BAP Solar Panel CEs) is based in Berlin."},
        "munich": {"status": "success", "report": "Maria (BAP Solar Panel CEs) is based in Munich."},
        "madrid": {"status": "success", "report": "Luis (BAP Solar Panel CEs) is based in Madrid."},
        "zurich": {"status": "success", "report": "Yariv (BAP Solar Panel CEs) is based in Zurich."},
        "paris": {"status": "success", "report": "Mathilde, Joël and Christophe (BAP Solar Panel CEs & TSC) are based in Paris."},
        "amsterdam": {"status": "success", "report": "Pulkit (BAP  Solar Panel CEs) is based in Amsterdam."},
        "copenhagen": {"status": "success", "report": "Christopher (BAP Solar Panel CEs) is based in Copenhagen."},
        "milan":  {"status": "success", "report": "Valentina (BAP Solar Panel CEs) will be based in Milan (soon)."},
        "dublin":  {"status": "success", "report": "Valentina (BAP Solar Panel CEs) is (still) based in Dublin."},
    }

    # Best Practice: Handle potential errors gracefully within the tool
    if city_normalized in mock_pm_db:
        return mock_pm_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have Customer Engineer information for '{city}'."}


# ----------------------- Sub Agents ------------------------------------

greeting_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="greeting_agent",
    instruction='''You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. 
        Do not engage in any other conversation or tasks. Transfer back to the parent agent without saying anything else.''',
    # Crucial for delegation: Clear description of capability
    description="Handles simple greetings and hellos",
)

# ----------------------- Create Agents ------------------------------------

"""Gets tools from MCP Server."""
# Get the credentials for the Maps API
SECRET="projects/bap-emea-apigee-5/secrets/adk-maps-apikeys/versions/latest"
secret_manager_client = SecretManagerClient()
maps_apikey_credential_str = secret_manager_client.get_secret(SECRET)

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='solar_bap_mcp',
    instruction='''You are a specialized assistance agent.
        You can help user, leverage the tools you have access to.
        Steps:
        - If the user gives a simple greeting (like 'Hi', 'Hello'), delegate to `greeting_agent`. 
        - Use the tool `apihub_toolset` to answer questions about solar panels.
        - Use the tool `connector_tool` to list sfdc contacts, companies and accounts and get details about them. 
            Crucial: When the user specifies 'company' or 'companies', interpret this as a request for 'Account' data for the connector_tool call. Generate a  Accounts request.
            Crucial: connector_tool accepts only one selection criterion per call. Therefore, if multiple criteria are given:
                - Select ONE for the Tool: Choose the highest-priority criterion (e.g., 'Industry' before 'Country') for the connector_tool call.
                - Filter Results Internally: Once connector_tool provides its output, you must then apply any remaining criteria to filter those results yourself.
            When a country filter is requested, use the 'BillingCountry' field for filtering.
        - Use the tool `integration_tool` to generate solar panels installation average quotation, depending on country. 
        - Use the tool `get_ce` to get the name of CE aka Customer Engineer present in a specified city. Ask for a city if not provided.
        - Handle yourself requests about mapping and directions using available tools.
        - For other queries, state clearly if you cannot handle them.
        - Transfer back to the parent agent without saying anything else.''',
    sub_agents=[greeting_agent],
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@modelcontextprotocol/server-google-maps",
                ],
                # Pass the API key as an environment variable to the npx process
                # This is how the MCP server for Google Maps expects the key.
                env={
                    "GOOGLE_MAPS_API_KEY": maps_apikey_credential_str
                }
            ),
            # You can filter for specific Maps tools if needed:
            # tool_filter=['get_directions', 'find_place_by_id']
        )
    ] + [get_ce, apihub_toolset, connector_tool, integration_tool],
)




