from google.cloud import discoveryengine_v1alpha as discoveryengine
from google.protobuf.json_format import ParseDict
import connector_app.config as config
import logging

import json
import os

# Load Identities
config_path = os.path.join(os.path.dirname(__file__), "../data/identities.json")
try:
    with open(config_path, "r") as f:
        USER_MAPPING = json.load(f)
except FileNotFoundError:
    logging.warning(f"Identity mapping file not found at {config_path}. Using empty mapping.")
    USER_MAPPING = {}

DOMAIN = "brendanhills.altostrat.com"

def map_identity(legacy_user):
    """Maps a legacy username (or role) to a Google Cloud Identity."""
    # Check direct mapping
    if legacy_user in USER_MAPPING:
        return USER_MAPPING[legacy_user]["google_id"]
    
    # Fallback to domain construction if it looks like a user
    if "." in legacy_user:
        return f"{legacy_user}@{DOMAIN}"
    
    # Fallback to group
    return f"group:{legacy_user}@{DOMAIN}"

class Indexer:
    def __init__(self, project_id=None, location=None):
        # Use config defaults if not provided
        self.project_id = project_id or config.PROJECT_ID
        self.location = location or config.LOCATION
        self.data_store_id = config.DATA_STORE_ID
        
        self.client_options = None
        if self.location != "global":
            api_endpoint = f"{self.location}-discoveryengine.googleapis.com"
            self.client_options = {"api_endpoint": api_endpoint}
            
        self.client = discoveryengine.DocumentServiceClient(client_options=self.client_options)
        self.parent = self.client.branch_path(
            project=self.project_id,
            location=self.location,
            data_store=self.data_store_id,
            branch="default_branch"
        )
        logging.info(f"Indexer initialized for Data Store: {self.data_store_id}")
        
    def process_and_push(self, item, item_type, dry_run=False):
        """
        Transforms a raw item into a Vertex AI Search Document and pushes it.
        """
        doc_id = item.get("id")
        if not doc_id:
            logging.warning(f"Item missing ID: {item}")
            return

        # 1. Construct ACL Info
        raw_acl = item.get("acl", [])
        principals = []
        
        for principle in raw_acl:
            mapped_id = map_identity(principle)
            if mapped_id.startswith("group:"):
                # Remove "group:" prefix for the API
                principals.append({"group_id": mapped_id.replace("group:", "")})
            else:
                principals.append({"user_id": mapped_id})
                
        # Structure for Google Cloud Discovery Engine ACL
        # readers is a list of AccessControlList, which has principals (list of Principal)
        acl_info = {
            "readers": [{"principals": principals}]
        }
        
        # 2. Construct Structured Data
        clean_item = {k: v for k, v in item.items() if k != "acl"}
        clean_item["type"] = item_type
        # Add a title field if main field is 'title' (common in search)
        # Ensure ID is also in struct data if needed by schema
        
        # URI Construction
        clean_item["uri"] = f"http://localhost:8501/?id={doc_id}"
        
        # 3. Create Document Object
        # Extract content for the main 'content' field if available
        # This satisfies CONTENT_REQUIRED and improves search relevance
        # Fallback to 'details' for Audit Logs
        page_content = clean_item.get("content") or clean_item.get("summary") or clean_item.get("details") or ""
        
        # If schema is strict about struct_data not having 'content' if it's in top-level, we might remove it
        # But usually duplication is fine or preferred for retention in structured result.
        
        document = discoveryengine.Document(
            id=doc_id,
            struct_data=clean_item,
            acl_info=acl_info,
            content=discoveryengine.Document.Content(
                mime_type="text/plain",
                raw_bytes=page_content.encode("utf-8")
            ) if page_content else None
        )
        
        if dry_run:
            print(f"--- Dry Run: {doc_id} ---")
            # Convert to dict for printing
            doc_dict = discoveryengine.Document.to_dict(document)
            import json
            print(json.dumps(doc_dict, indent=2))
            return 
        
        # 4. Push to Vertex AI Search
        self._push_document(document)
        
    def _push_document(self, document):
        try:
            # unique resource name for the document
            # projects/{project}/locations/{location}/collections/{collection}/dataStores/{data_store}/branches/{branch}/documents/{document_id}
            # We must set name explicitly if not already set, or rely on parent + id logic. 
            # Ideally we construct the full name.
            
            # The client library often requires the 'name' field to be set on the document for update_document
            if not document.name:
                document.name = f"{self.parent}/documents/{document.id}"
            
            request = discoveryengine.UpdateDocumentRequest(
                document=document,
                allow_missing=True
            )
            self.client.update_document(request=request)
            logging.info(f"Successfully pushed document: {document.id}")
        except Exception as e:
            logging.error(f"Failed to push document {document.id}: {e}")
