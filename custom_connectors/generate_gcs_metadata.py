import json
import os

# Configuration
BUCKET_NAME = "uk-bh-experiments-argolis-content" # We will create this
OUTPUT_FILE = "gcs_content/metadata.jsonl"
DOMAIN = "brendanhills.altostrat.com"

# Define ACLs for the generated files
# Map filenames (relative to bucket root) to roles/users
FILE_ACLS = {
    # Restricted
    "restricted/Board_Minutes_Q1_2024.pdf": ["cathy.compliance", "edward.exec"],
    
    # Internal
    "internal/Project_Titan_Proposal.pdf": ["ian.ibanker", "tim.trader", "brendan"], # Internal usually broadly accesssible, but let's be explicit
    
    # Public
    "public/Press_Release_2024_01.txt": [] # Empty list = Public? Or AllUsers? 
    # For Vertex AI Search GCS, omitting 'acl' usually means inheriting bucket-level, 
    # but for granular control we might want to be explicit. 
    # Let's treat Public as "no restriction" which usually means not adding specific readers 
    # if the data store allows it, OR adding "all_users" group.
}

def generate_metadata():
    with open(OUTPUT_FILE, "w") as f:
        for filepath, users in FILE_ACLS.items():
            gcs_uri = f"gs://{BUCKET_NAME}/{filepath}"
            
            # If public, we might skip ACL or add specific public group
            if "public" in filepath:
                # For public files, we can just skip adding the ACL field 
                # (assuming the Data Store isn't strictly closed) 
                # OR add a wide group.
                metadata = {
                    "id": filepath,
                    "structData": {"sensitivity": "Public"},
                    "content": {"mimeType": "text/plain", "uri": gcs_uri}
                }
            else:
                # Construct Readers List
                readers = []
                for user in users:
                    readers.append({
                        "principals": [{"user_id": f"{user}@{DOMAIN}"}]
                    })
                
                metadata = {
                    "id": filepath,
                    "aclInfo": {"readers": readers},
                    "structData": {"sensitivity": "Restricted" if "restricted" in filepath else "Internal"},
                    "content": {"mimeType": "application/pdf", "uri": gcs_uri}
                }
            
            json_line = json.dumps(metadata)
            f.write(json_line + "\n")
            
    print(f"Generated Metadata: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_metadata()
