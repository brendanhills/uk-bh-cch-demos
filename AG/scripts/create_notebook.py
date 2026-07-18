#!/usr/bin/env python3
"""
Educational script demonstrating how to create a notebook using the NotebookLM API.
Under the hood, this makes a POST request to:
https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks
"""

import os
import sys
from dotenv import load_dotenv

# Ensure the root folder is on Python path so we can import notebooklm_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notebooklm_client import NotebookLMClient

def main():
    # Load configurations from .env
    load_dotenv()
    
    project_number = os.getenv("GCP_PROJECT_NUMBER", "123456789012")
    location = os.getenv("GCP_LOCATION", "global")
    endpoint_location = os.getenv("GCP_ENDPOINT_LOCATION", "us")
    token = os.getenv("GCP_ACCESS_TOKEN")
    mode = os.getenv("DEFAULT_MODE", "mock")
    verbose = os.getenv("VERBOSE_LOGGING", "True").lower() == "true"

    print("\033[96m========================================================================\033[0m")
    print("\033[96mLEARNING SCRIPT: Creating a Notebook via REST API\033[0m")
    print("\033[96m========================================================================\033[0m")
    print("REST Endpoints and JSON Schemas:")
    print("  - Path: /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks")
    print("  - HTTP Method: POST")
    print("  - Payload JSON Schema:")
    print("    {")
    print('      "title": "<NOTEBOOK_TITLE>"')
    print("    }")
    print("========================================================================\n")

    # Initialize Client
    client = NotebookLMClient(
        project_number=project_number,
        location=location,
        endpoint_location=endpoint_location,
        token=token,
        default_mode=mode,
        verbose=verbose
    )

    title = "Machine Learning Study Notes"
    print(f"Creating notebook with title: '{title}'...")
    
    try:
        notebook = client.create_notebook(title=title)
        
        notebook_id = notebook["notebookId"]
        resource_name = notebook["name"]
        
        print("\n\033[92m✔ Execution Complete!\033[0m")
        print(f"Created Notebook ID: {notebook_id}")
        print(f"Complete Resource Name: {resource_name}")
        print(f"User Role: {notebook['metadata']['userRole']}")
        
    except Exception as e:
        print(f"\n\033[91m✘ Failed to create notebook: {e}\033[0m")

if __name__ == "__main__":
    main()
