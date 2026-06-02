#!/usr/bin/env python3
"""
Educational script demonstrating how to add sources in a batch to an existing notebook.
Under the hood, this makes a POST request to:
https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:batchCreate
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
    print("\033[96mLEARNING SCRIPT: Batch Creating Notebook Sources via REST API\033[0m")
    print("\033[96m========================================================================\033[0m")
    print("REST Endpoints and JSON Schemas:")
    print("  - Path: /v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:batchCreate")
    print("  - HTTP Method: POST")
    print("  - Request JSON Payload structure (can include one content type per list item):")
    print("    {")
    print('      "userContents": [')
    print('        { "textContent": { "sourceName": "...", "content": "..." } },')
    print('        { "webContent": { "url": "...", "sourceName": "..." } },')
    print('        { "videoContent": { "youtubeUrl": "..." } },')
    print('        { "googleDriveContent": { "documentId": "...", "mimeType": "...", "sourceName": "..." } }')
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

    # First, create a notebook to add sources to
    print("Creating a temporary notebook...")
    notebook = client.create_notebook(title="Sources Demonstration Notebook")
    notebook_id = notebook["notebookId"]

    # Formulate different sources to add in batch
    sources_to_add = [
        # 1. Raw Text Content
        {
            "textContent": {
                "sourceName": "Project Requirements Overview",
                "content": "NotebookLM Enterprise API allows developers to programmatically load knowledge documents into a shared space. It integrates Google Docs, PDFs, websites and audios to provide high-quality summaries and conversational synthesis."
            }
        },
        # 2. Web URL Content
        {
            "webContent": {
                "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "sourceName": "Wikipedia: Artificial Intelligence"
            }
        },
        # 3. YouTube Video Content
        {
            "videoContent": {
                "youtubeUrl": "https://www.youtube.com/watch?v=zjkBMFhNj_g"
            }
        }
    ]

    print(f"\nAdding {len(sources_to_add)} sources to notebook ID {notebook_id} in a single batch call...")
    
    try:
        response = client.batch_create_sources(notebook_id=notebook_id, sources_list=sources_to_add)
        
        print("\n\033[92m✔ Execution Complete!\033[0m")
        print("Created Sources Metadata:")
        for idx, src in enumerate(response.get("sources", [])):
            s_id = src["sourceId"]["id"]
            s_title = src["title"]
            s_status = src["settings"]["status"]
            print(f"  [{idx+1}] ID: {s_id} | Title: '{s_title}' | Status: {s_status}")
            
    except Exception as e:
        print(f"\n\033[91m✘ Failed to batch create sources: {e}\033[0m")

if __name__ == "__main__":
    main()
