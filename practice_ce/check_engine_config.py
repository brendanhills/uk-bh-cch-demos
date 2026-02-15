from google.cloud import discoveryengine
import connector_app.config as config
import logging

logging.basicConfig(level=logging.INFO)

def check_engine_config(project_id, location):
    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}
        
    client = discoveryengine.EngineServiceClient(client_options=client_options)
    
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    
    print(f"Listing Engines in {parent}...")
    request = discoveryengine.ListEnginesRequest(parent=parent)
    page_result = client.list_engines(request=request)
    
    for engine in page_result:
        print(f"Engine: {engine.name}")
        print(f"  Display Name: {engine.display_name}")
        print(f"  Data Stores: {engine.data_store_ids}")
        print("---")

if __name__ == "__main__":
    check_engine_config(config.PROJECT_ID, config.LOCATION)
