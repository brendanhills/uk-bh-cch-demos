from google.cloud import discoveryengine_v1alpha as discoveryengine
import connector_app.config as config
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_document_acl(project_id, location, data_store_id, doc_id):
    client_options = None
    if location != "global":
        api_endpoint = f"{location}-discoveryengine.googleapis.com"
        client_options = {"api_endpoint": api_endpoint}

    client = discoveryengine.DocumentServiceClient(client_options=client_options)

    name = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    ) + f"/documents/{doc_id}"

    logging.info(f"Fetching document: {name}...")
    try:
        request = discoveryengine.GetDocumentRequest(name=name)
        document = client.get_document(request=request)
        
        logging.info(f"Document Found: {document.id}")
        logging.info(f"Title: {document.struct_data.get('title')}")
        logging.info(f"Sensitivity: {document.struct_data.get('sensitivity')}")
        
        if document.acl_info:
            logging.info("--- ACL INFO ---")
            for reader in document.acl_info.readers:
                for principal in reader.principals:
                    if principal.user_id:
                        logging.info(f"User: {principal.user_id}")
                    elif principal.group_id:
                        logging.info(f"Group: {principal.group_id}")
            logging.info("--- END ACL ---")
        else:
            logging.warning("No ACL Info found! (This implies PUBLIC access or configuration error)")
            
    except Exception as e:
        logging.error(f"Failed to fetch document: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_document_acl(config.PROJECT_ID, config.LOCATION, config.DATA_STORE_ID, "TR-004")
