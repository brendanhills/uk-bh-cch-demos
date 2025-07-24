from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset

import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

BAP_PROJECT_ID = os.getenv("BAP_PROJECT_ID","")
BAP_LOCATION = os.getenv("BAP_LOCATION","")
SALESFORCE_CONNECTOR_ID = os.getenv("SALESFORCE_CONNECTOR_ID","cl-salesforce")
SOLAR_CONNECTOR_ID = os.getenv("SOLAR_CONNECTOR_ID", "cl-quoteSolar")


# ----------------------- Integration Connector Tool ------------------------------------

connector_tool = ApplicationIntegrationToolset(
    project=BAP_PROJECT_ID, 
    location=BAP_LOCATION, 
    connection=SALESFORCE_CONNECTOR_ID, 
    entity_operations={"Account": ["UPDATE","LIST","GET"], "Contact": ["LIST","GET"]}, 
    #service_account_credentials='{...}', # optional
    #tool_name="tool_AppInt1",
    tool_instructions="Use this tool to provide information about salesforce contacts, companies and accounts. Use page size 1000. Sort by Name. Crucial: If you have several selection criterions, keep only the first one"
)

# ----------------------- Application Integration Tool ------------------------------------

#integration_tool = ApplicationIntegrationToolset(
#    project=BAP_PROJECT_ID, 
#    location=BAP_LOCATION, 
#    integration=SOLAR_CONNECTOR_ID, 
#    #trigger="api_trigger/QuoteGenerationWorkflow_API_1", 
#    #service_account_credentials='{...}', #optional
#    #tool_name="tool_AppInt2",
#    tool_instructions="Use this tool to get solar panels installation quotation, depending on country"
#)
