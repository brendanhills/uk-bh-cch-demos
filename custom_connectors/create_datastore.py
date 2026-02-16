import sys
from google.cloud import discoveryengine_v1alpha as discoveryengine
from connector_app import config

def create_data_store():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    data_store_id = config.DATA_STORE_ID
    display_name = config.DATA_STORE_DISPLAY_NAME

    # Configure Client Options for Regional Endpoint
    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}

    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    
    # Configure ACLs (Identity Provider)
    # Use GSUITE (Cloud Identity) as the IDP
    idp_config = discoveryengine.IdpConfig(
        idp_type=discoveryengine.IdpConfig.IdpType.GSUITE
    )

    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        acl_enabled=True,
        idp_config=idp_config
    )

    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store=data_store,
        data_store_id=data_store_id
    )

    print(f"Creating Data Store: {data_store_id} in {parent}...")
    try:
        operation = client.create_data_store(request=request)
        response = operation.result()
        print(f"Data Store Created: {response.name}")
        return response
    except Exception as e:
        print(f"Error creating Data Store: {e}")
        # Check if already exists
        if "already exists" in str(e):
             print("Data Store already exists. Proceeding...")
             return None
        sys.exit(1)

if __name__ == "__main__":
    create_data_store()
