#!/usr/bin/env python3
"""
Educational script demonstrating how to delete notebooks and sources.
Under the hood, notebook deletion makes a POST request to:
https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks:batchDelete
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
    print("\033[96mLEARNING SCRIPT: Notebook and Sources Deletion via REST API\033[0m")
    print("\033[96m========================================================================\033[0m")
    print("REST Endpoints and JSON Schemas:")
    print("  - Notebook Deletion Path: /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks:batchDelete")
    print("  - Notebook Deletion Method: POST")
    print("  - Notebook Deletion Payload:")
    print("    {")
    print('      "names": [')
    print('        "projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}"')
    print("      ]")
    print("    }")
    print("\n  - Sources Deletion Path: /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:batchDelete")
    print("  - Sources Deletion Method: POST")
    print("  - Sources Deletion Payload:")
    print("    {")
    print('      "names": [')
    print('        "projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/source/{SOURCE_ID}"')
    print("      ]")
    print("    }")
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
    print("Creating a temporary notebook to delete...")
    notebook = client.create_notebook(title="Short Lived Notebook")
    notebook_id = notebook["notebookId"]

    # 2. Add a text source
    print("\nAdding a source that will be deleted first...")
    sources_to_add = [{"textContent": {"sourceName": "Temp Doc", "content": "Delete me."}}]
    sources_response = client.batch_create_sources(notebook_id=notebook_id, sources_list=sources_to_add)
    source_resource_name = sources_response["sources"][0]["name"]
    source_id = sources_response["sources"][0]["sourceId"]["id"]

    # 3. Delete the Source
    print(f"\nDeleting source ID {source_id} (Resource Name: {source_resource_name})...")
    try:
        client.delete_sources(notebook_id=notebook_id, source_resource_names=[source_resource_name])
        print("✔ Source successfully deleted.")
    except Exception as e:
        print(f"✘ Failed to delete source: {e}")

    # 4. Delete the Notebook
    print(f"\nDeleting notebook ID {notebook_id} (Batch deleting resource name)...")
    try:
        client.delete_notebook(notebook_id=notebook_id)
        print("\n\033[92m✔ Execution Complete!\033[0m")
        print(f"Successfully deleted notebook ID {notebook_id}.")
    except Exception as e:
        print(f"\n\033[91m✘ Failed to delete notebook: {e}\033[0m")

if __name__ == "__main__":
    main()
