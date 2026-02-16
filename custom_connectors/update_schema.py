from google.cloud import discoveryengine_v1beta as discoveryengine
import json
import time

def update_schema():
    # Use v1beta for schema updates as it has more features/stability for this sometimes
    # But using v1 is also fine. Let's stick to what we imported or v1beta if v1 fails.
    # Actually, the client library naming is tricky. 
    # Let's use the one that works with the client_options.
    
    project_id = "uk-bh-experiments-argolis"
    location = "us"
    data_store_id = "cebank-compliance-store-v4"
    
    client_options = {"api_endpoint": f"{location}-discoveryengine.googleapis.com"}
    client = discoveryengine.SchemaServiceClient(client_options=client_options)
    
    schema_name = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{data_store_id}/schemas/default_schema"
    
    with open("data/schema.json", "r") as f:
        schema_dict = json.load(f)
    
    # Construct the Schema object
    # The API expects 'json_schema' as a string field inside the Schema object
    schema = discoveryengine.Schema(
        name=schema_name,
        json_schema=json.dumps(schema_dict)
    )
    
    request = discoveryengine.UpdateSchemaRequest(
        schema=schema,
        allow_missing=True
    )
    
    print(f"Updating schema: {schema_name}")
    try:
        operation = client.update_schema(request=request)
        print("Waiting for operation to complete...")
        response = operation.result(timeout=300)
        print("Schema updated successfully!")
        print(response)
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
