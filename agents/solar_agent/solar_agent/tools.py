from google.adk.tools.apihub_tool.apihub_toolset import APIHubToolset
from google.adk.tools.apihub_tool.clients.secret_client import SecretManagerClient
from google.adk.tools.openapi_tool.auth.auth_helpers import token_to_scheme_credential
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset


PROJECT_ID="bap-emea-apigee-5"
LOCATION="europe-west1"

# ----------------------- Integration Connector Tool ------------------------------------

connector_tool = ApplicationIntegrationToolset(
    project=f"{PROJECT_ID}", 
    location=f"{LOCATION}", 
    connection="cl-salesforce", 
    entity_operations={"Account": ["UPDATE","LIST","GET"], "Contact": ["LIST","GET"]}, 
    #service_account_credentials='{...}', # optional
    #tool_name="tool_AppInt1",
    tool_instructions="Use this tool to provide information about salesforce contacts, companies and accounts. Use page size 1000. Sort by Name. Crucial: If you have several selection criterions, keep only the first one"
)

# ----------------------- Application Integration Tool ------------------------------------

integration_tool = ApplicationIntegrationToolset(
    project=f"{PROJECT_ID}", 
    location=f"{LOCATION}", 
    integration="cl-quoteSolar", 
    #trigger="api_trigger/QuoteGenerationWorkflow_API_1", 
    #service_account_credentials='{...}', #optional
    #tool_name="tool_AppInt2",
    tool_instructions="Use this tool to get solar panels installation quotation, depending on country"
)

# ----------------------- API Hub Tool ------------------------------------

API_HUB_LOCATION=f"projects/{PROJECT_ID}/locations/{LOCATION}/apis"
SECRET=f"projects/{PROJECT_ID}/secrets/adk-apikeys/versions/latest"

# Get the credentials for the Solar Service API
secret_manager_client = SecretManagerClient()
apikey_credential_str = secret_manager_client.get_secret(SECRET)

auth_scheme, auth_credential = token_to_scheme_credential("apikey", "header", "x-api-key", apikey_credential_str)

apihub_toolset = APIHubToolset(
    name="apihub-sample-tool",
    description="Sample Tool",
    apihub_resource_name=f"{API_HUB_LOCATION}/bap-emea-apigee-5-Solar-Service-v1", # API Hub resource name
    auth_scheme=auth_scheme,
    auth_credential=auth_credential,
)
