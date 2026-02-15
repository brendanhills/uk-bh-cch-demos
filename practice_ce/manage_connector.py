import argparse
import logging
import sys
import subprocess
from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.api_core.client_options import ClientOptions
from google.protobuf.field_mask_pb2 import FieldMask
import connector_app.config as config

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_client(service_type="DataStore"):
    project_id = config.PROJECT_ID
    location = config.LOCATION
    
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    
    if service_type == "DataStore":
        return discoveryengine.DataStoreServiceClient(client_options=client_options)
    elif service_type == "Engine":
        return discoveryengine.EngineServiceClient(client_options=client_options)
    
    raise ValueError(f"Unknown service type: {service_type}")

def create_data_store():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    data_store_id = config.DATA_STORE_ID
    display_name = config.DATA_STORE_DISPLAY_NAME
    
    client = get_client("DataStore")
    
    logging.info(f"Creating Data Store '{data_store_id}' in {project_id}/{location}...")
    
    # Check if exists
    name = client.data_store_path(project=project_id, location=location, data_store=data_store_id)
    try:
        client.get_data_store(name=name)
        logging.info("Data Store already exists.")
        return
    except Exception:
        logging.info("Data Store not found. Creating...")

    parent = client.collection_path(project=project_id, location=location, collection="default_collection")
    
    ds_obj = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.NO_CONTENT,
        acl_enabled=True,
    )

    operation = client.create_data_store(
        parent=parent,
        data_store=ds_obj,
        data_store_id=data_store_id
    )

    logging.info("Waiting for creation...")
    response = operation.result()
    logging.info(f"Data Store created: {response.name}")

def delete_data_store():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    data_store_id = config.DATA_STORE_ID
    
    client = get_client("DataStore")
    
    name = client.data_store_path(project=project_id, location=location, data_store=data_store_id)
    logging.info(f"Deleting Data Store '{data_store_id}'...")
    
    try:
        operation = client.delete_data_store(name=name)
        logging.info("Waiting for deletion...")
        operation.result()
        logging.info("Data Store deleted.")
    except Exception as e:
        logging.error(f"Failed to delete (or not found): {e}")

def link_engine():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    engine_id = config.ENGINE_ID
    data_store_id = config.DATA_STORE_ID
    
    if not engine_id:
        logging.error("ENGINE_ID not set in config.py")
        return

    client = get_client("Engine")
    
    engine_name = client.engine_path(
        project=project_id,
        location=location,
        collection="default_collection",
        engine=engine_id
    )
    
    logging.info(f"Linking Data Store '{data_store_id}' to Engine '{engine_id}'...")
    
    try:
        engine = client.get_engine(name=engine_name)
        current_ids = list(engine.data_store_ids)
        logging.info(f"Current Data Store IDs: {current_ids}")
        
        if data_store_id in current_ids:
            logging.info("Data Store already linked.")
            return

        new_ids = []
        # Cleanup old versions of our store
        for ds_id in current_ids:
            if "cebank-compliance-store-v" in ds_id and ds_id != data_store_id:
                logging.info(f"Removing old version: {ds_id}")
                continue
            new_ids.append(ds_id)
            
        new_ids.append(data_store_id)
        
        logging.info(f"Updating Engine with new IDs: {new_ids}")
        
        engine.data_store_ids = new_ids
        update_mask = FieldMask(paths=["data_store_ids"])
        
        op = client.update_engine(
            engine=engine,
            update_mask=update_mask
        )
        
        if hasattr(op, "result"):
            logging.info("Waiting for update operation...")
            response = op.result()
        else:
            response = op
            
        logging.info(f"Engine updated. Linked Data Stores: {response.data_store_ids}")
        
    except Exception as e:
        logging.error(f"Failed to link engine: {e}")

def list_engines():
    project_id = config.PROJECT_ID
    location = config.LOCATION
    
    client = get_client("Engine")
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    
    print(f"Listing engines in {parent}...")
    try:
        response = client.list_engines(parent=parent)
        for engine in response:
            print(f"Engine: {engine.name}")
            print(f"  Display Name: {engine.display_name}")
            print(f"  DataStore IDs: {engine.data_store_ids}")
            print("-" * 20)
    except Exception as e:
        print(f"Error listing engines: {e}")

def run_sync():
    logging.info("Running Connector Sync...")
    try:
        subprocess.run([sys.executable, "-m", "connector_app.main"], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Sync failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage Gemini Enterprise Custom Connector")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("create", help="Create Data Store (ACL enabled)")
    subparsers.add_parser("delete", help="Delete Data Store")
    subparsers.add_parser("link", help="Link Data Store to Engine")
    subparsers.add_parser("list", help="List available Engines")
    subparsers.add_parser("sync", help="Run Connector Sync (Push Documents)")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_data_store()
    elif args.command == "delete":
        delete_data_store()
    elif args.command == "link":
        link_engine()
    elif args.command == "list":
        list_engines()
    elif args.command == "sync":
        run_sync()

if __name__ == "__main__":
    main()
