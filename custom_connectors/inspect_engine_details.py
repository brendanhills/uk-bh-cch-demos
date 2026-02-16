from google.cloud import discoveryengine_v1alpha as discoveryengine
import connector_app.config as config
import json
from google.protobuf.json_format import MessageToDict

def inspect_engine():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    engine_id = config.ENGINE_ID

    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}

    client = discoveryengine.EngineServiceClient(client_options=client_options)
    name = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}"

    print(f"Inspecting Engine: {name}")
    try:
        engine = client.get_engine(name=name)
        # Convert to dict for readability and to see all fields including empty ones if possible (MessageToDict defaults)
        engine_dict = MessageToDict(engine._pb)
        print(json.dumps(engine_dict, indent=2))
        
        # Specifically check common config
        if hasattr(engine, 'chat_engine_config'):
             print("\n--- Chat Engine Config ---")
             print(engine.chat_engine_config)
        
        if hasattr(engine, 'common_config'):
             print("\n--- Common Config ---")
             print(engine.common_config)

    except Exception as e:
        print(f"Error getting engine: {e}")

if __name__ == "__main__":
    inspect_engine()
