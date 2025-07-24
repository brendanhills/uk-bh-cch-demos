
from .tools import connector_tool#, integration_tool
from google.adk.agents import Agent
from vertexai.preview.reasoning_engines import AdkApp
import os
from dotenv import load_dotenv


load_dotenv(verbose=True)

MODEL = os.getenv("MODEL","gemini-2.5-flash")

# ----------------------- Python Code Tool ------------------------------------

# ----------------------- Create Agents ------------------------------------

root_agent = Agent(
    model=MODEL,
    name='solar_bap_salesforce_agent',
    description=('Agent to connect to salesforce and return customer information as well as solar panels quotation'),
    instruction='''You are a specialized assistance agent.
        You can help user, leverage the tools you have access to.
        Steps:
        - Use the tool `connector_tool` to list sfdc contacts, companies and accounts and get details about them. 
            Crucial: When the user specifies 'company' or 'companies', interpret this as a request for 'Account' data for the connector_tool call. Generate a  Accounts request.
            Crucial: connector_tool accepts only one selection criterion per call. Therefore, if multiple criteria are given:
                - Select ONE for the Tool: Choose the highest-priority criterion (e.g., 'Industry' before 'Country') for the connector_tool call.
                - Filter Results Internally: Once connector_tool provides its output, you must then apply any remaining criteria to filter those results yourself.
            When a country filter is requested, use the 'BillingCountry' field for filtering.
        - Use the tool `integration_tool` to generate solar panels installation average quotation, depending on country. 
        - For other queries, state clearly if you cannot handle them.
        - Transfer back to the parent agent without saying anything else.''',
    tools=[connector_tool]
)
app = AdkApp(agent=root_agent)