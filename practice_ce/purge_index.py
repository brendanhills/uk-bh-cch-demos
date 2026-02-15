from google.cloud import discoveryengine_v1alpha as discoveryengine
import connector_app.config as config
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def purge_index(project_id, location, data_store_id):
    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}

    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    logging.info(f"Purging ALL documents from {parent}...")
    
    # Use PurgeDocumentsRequest with wildcard filter
    request = discoveryengine.PurgeDocumentsRequest(
        parent=parent,
        filter="*", # Delete EVERYTHING
        force=True
    )
    
    try:
        operation = client.purge_documents(request=request)
        logging.info("Waiting for purge operation to complete...")
        response = operation.result()
        logging.info(f"Purge complete. Purge count: {response.purge_count}")
        
    except Exception as e:
        logging.error(f"Purge failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    purge_index(config.PROJECT_ID, config.LOCATION, config.DATA_STORE_ID)
