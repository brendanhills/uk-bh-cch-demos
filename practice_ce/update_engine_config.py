from google.cloud import discoveryengine_v1alpha as discoveryengine
import connector_app.config as config

def update_engine():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    engine_id = config.ENGINE_ID
    
    # New Display Name
    NEW_DISPLAY_NAME = "GE Agents Demo"

    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}

    client = discoveryengine.EngineServiceClient(client_options=client_options)
    name = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}"

    print(f"Updating Engine: {name}")
    print(f"Setting Display Name to: {NEW_DISPLAY_NAME}")
    
    try:
        # Get current engine
        engine = client.get_engine(name=name)
        
        # Update display_name
        engine.display_name = NEW_DISPLAY_NAME
        
        # Update request
        # Mask is required to specify what fields to update
        update_mask = {"paths": ["display_name"]}
        
        # update_engine typically returns the Engine directly in v1/v1alpha unless it's an LRO
        operation = client.update_engine(request=discoveryengine.UpdateEngineRequest(engine=engine, update_mask=update_mask))
        
        print(f"Engine Updated Successfully.")
        print(f"New Display Name: {operation.display_name}")

    except Exception as e:
        print(f"Error updating engine: {e}")

if __name__ == "__main__":
    update_engine()
