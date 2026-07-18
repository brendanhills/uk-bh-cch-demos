#!/usr/bin/env python3
"""
Educational script demonstrating how to stream-upload a local binary file (PDF, TXT, MD, etc.)
directly as a source inside a notebook.
Under the hood, this makes a POST request to:
https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/upload/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:uploadFile
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
    print("\033[96mLEARNING SCRIPT: Streaming Local File Upload as a Source via REST API\033[0m")
    print("\033[96m========================================================================\033[0m")
    print("REST Endpoints and HTTP Details:")
    print("  - Path: /upload/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks/{NOTEBOOK_ID}/sources:uploadFile")
    print("  - HTTP Method: POST")
    print("  - Custom HTTP Headers Required:")
    print("    - X-Goog-Upload-File-Name: <DISPLAY_NAME_IN_NOTEBOOK>")
    print("    - X-Goog-Upload-Protocol: raw")
    print("    - Content-Type: <MIME_TYPE> (e.g. application/pdf, text/plain)")
    print("  - Request Body: Raw Binary File Payload (equivalent to curl's --data-binary)")
    print("========================================================================\n")

    client = NotebookLMClient(
        project_number=project_number,
        location=location,
        endpoint_location=endpoint_location,
        token=token,
        default_mode=mode,
        verbose=verbose
    )

    # 1. Create a notebook
    print("Creating a temporary notebook...")
    notebook = client.create_notebook(title="File Streaming Upload Notebook")
    notebook_id = notebook["notebookId"]

    # 2. Create a temporary local text file for streaming upload
    temp_filename = "dummy_study_guide.txt"
    with open(temp_filename, "w") as f:
        f.write("Deep Learning Study Guide\n")
        f.write("=========================\n")
        f.write("1. Neural Networks contain input layers, hidden layers, and output layers.\n")
        f.write("2. Backpropagation calculates the gradient of the loss function using chain rule.\n")
        f.write("3. Optimizers like Adam and SGD update neural weights recursively to minimize loss.\n")
    
    print(f"\nCreated local dummy file: '{temp_filename}' ({os.path.getsize(temp_filename)} bytes)")

    try:
        # 3. Stream Upload File
        display_name = "Deep Learning Study Guide"
        content_type = "text/plain"
        
        print(f"Uploading '{temp_filename}' as source '{display_name}' ({content_type})...")
        
        response = client.upload_source_file(
            notebook_id=notebook_id,
            file_path=temp_filename,
            display_name=display_name,
            content_type=content_type
        )
        
        source_id = response["sourceId"]["id"]
        
        print("\n\033[92m✔ Execution Complete!\033[0m")
        print(f"Successfully uploaded file!")
        print(f"Assigned Source ID: {source_id}")
        
    except Exception as e:
        print(f"\n\033[91m✘ Failed to upload file: {e}\033[0m")
        
    finally:
        # Clean up temporary local file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            print(f"\nCleaned up local dummy file: '{temp_filename}'")

if __name__ == "__main__":
    main()
