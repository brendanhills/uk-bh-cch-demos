#!/usr/bin/env python3
"""
Educational script demonstrating how to share a notebook with other enterprise users.
Under the hood, this makes a POST request to:
https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}:share
"""

import os
import sys
from dotenv import load_dotenv

# Ensure the root folder is on Python path so we can import notebooklm_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notebooklm_client import NotebookLMClient

def main():
    load_dotenv()
    
    project_number = os.getenv("GCP_PROJECT_NUMBER", "123456789012")
    location = os.getenv("GCP_LOCATION", "global")
    endpoint_location = os.getenv("GCP_ENDPOINT_LOCATION", "us")
    token = os.getenv("GCP_ACCESS_TOKEN")
    mode = os.getenv("DEFAULT_MODE", "mock")
    verbose = os.getenv("VERBOSE_LOGGING", "True").lower() == "true"

    print("\033[96m========================================================================\033[0m")
    print("\033[96mLEARNING SCRIPT: Sharing a Notebook / Assigning Access Roles via REST API\033[0m")
    print("\033[96m========================================================================\033[0m")
    print("REST Endpoints and JSON Schemas:")
    print("  - Path: /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}:share")
    print("  - HTTP Method: POST")
    print("  - Payload JSON Schema:")
    print("    {")
    print('      "accountAndRoles": [')
    print('        {')
    print('          "email": "<USER_EMAIL_ADDRESS>",')
    print('          "role": "<PROJECT_ROLE>"')
    print("        }")
    print("      ]")
    print("    }")
    print("\nSupported Roles:")
    print("  - PROJECT_ROLE_OWNER      : Direct owner of the notebook")
    print("  - PROJECT_ROLE_WRITER     : Can edit notebook and add/remove sources")
    print("  - PROJECT_ROLE_READER     : Can read/view notebook and sources")
    print("  - PROJECT_ROLE_NOT_SHARED : Removes all access from the user")
    print("========================================================================\n")

    client = NotebookLMClient(
        project_number=project_number,
        location=location,
        endpoint_location=endpoint_location,
        token=token,
        default_mode=mode,
        verbose=verbose
    )

    # 1. Create notebook
    print("Creating a temporary notebook...")
    notebook = client.create_notebook(title="Collaborative Project Notebook")
    notebook_id = notebook["notebookId"]

    # 2. Formulate sharing roles
    sharing_payload = [
        {
            "email": "sarah.editor@enterprise.com",
            "role": "PROJECT_ROLE_WRITER"
        },
        {
            "email": "david.viewer@enterprise.com",
            "role": "PROJECT_ROLE_READER"
        }
    ]

    print(f"\nSharing notebook ID {notebook_id} with Sarah (Writer) and David (Reader)...")
    
    try:
        client.share_notebook(notebook_id=notebook_id, accounts_and_roles=sharing_payload)
        
        print("\n\033[92m✔ Execution Complete!\033[0m")
        print("Successfully assigned sharing roles. Sarah can now edit the notebook, and David can view it.")
        
        # In Mock Mode, retrieve the notebook to verify metadata has updated isShared flag
        if mode == "mock":
            print("\nRetrieving notebook details to verify state change...")
            updated_nb = client.get_notebook(notebook_id=notebook_id)
            print(f"  Notebook title: '{updated_nb['title']}'")
            print(f"  Is Shared: {updated_nb['metadata']['isShared']}")
            
    except Exception as e:
        print(f"\n\033[91m✘ Failed to share notebook: {e}\033[0m")

if __name__ == "__main__":
    main()
