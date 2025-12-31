import os
import random
import string
import urllib.request
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
from google.api_core import exceptions


def create_gcs_bucket(project_id: str, bucket_name: str, location: str):
    """Creates a new GCS bucket."""
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.create_bucket(bucket_name, location=location)
        print(f"--- Bucket {bucket.name} created in {location} ---")
        return bucket
    except exceptions.Conflict:
        print(f"--- Bucket {bucket_name} already exists. ---")
        return storage_client.get_bucket(bucket_name)


def upload_sample_files(bucket_name: str):
    """Uploads sample files to the GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Create and upload dummy.txt
    dummy_content = "This is a dummy file for testing purposes."
    dummy_blob = bucket.blob("dummy.txt")
    dummy_blob.upload_from_string(dummy_content)
    print(f"--- Uploaded dummy.txt to {bucket_name} ---")

    # Download and upload PDF files
    pdf_urls = [
        "https://services.google.com/fh/files/misc/ai_agents_handbook.pdf",
        "https://services.google.com/fh/files/misc/gemini-for-google-workspace-prompting-guide-101.pdf",
    ]
    for url in pdf_urls:
        file_name = url.split("/")[-1]
        try:
            with urllib.request.urlopen(url) as response:
                pdf_content = response.read()
                pdf_blob = bucket.blob(file_name)
                pdf_blob.upload_from_string(pdf_content, content_type="application/pdf")
                print(f"--- Uploaded {file_name} to {bucket_name} ---")
        except Exception as e:
            print(f"--- Failed to download or upload {file_name}: {e} ---")



def create_gcs_datastore(project_id: str, location: str, data_store_id: str):
    """Creates a GCS data store."""
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    data_store = discoveryengine.DataStore(
        display_name=f"{data_store_id}-ds",
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    # Explicitly set the regional endpoint to match the resource location
    client_options = {"api_endpoint": f"{location}-discoveryengine.googleapis.com"}
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    try:
        operation = client.create_data_store(
            parent=parent,
            data_store=data_store,
            data_store_id=data_store_id,
        )
        print(f"--- Waiting for GCS datastore to create: {data_store_id} ---")
        response = operation.result()
        print(f"--- GCS datastore created: {response.name} ---")
        return response
    except exceptions.AlreadyExists:
        print(f"--- GCS datastore {data_store_id} already exists. ---")
        return client.get_data_store(name=f"{parent}/dataStores/{data_store_id}")


def import_from_gcs(
    project_id: str, location: str, data_store_id: str, gcs_bucket_name: str
):
    """Imports documents from a GCS bucket into a data store."""
    # Explicitly set the regional endpoint to match the resource location
    client_options = {"api_endpoint": f"{location}-discoveryengine.googleapis.com"}
    client = discoveryengine.DocumentServiceClient(client_options=client_options)
    
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        branch="default_branch",
    )

    # The gcs_uri should be in the format `gs://<bucket_name>/*` to import all files
    gcs_uri = f"gs://{gcs_bucket_name}/*"

    request = discoveryengine.ImportDocumentsRequest(
        parent=parent,
        gcs_source=discoveryengine.GcsSource(input_uris=[gcs_uri]),
        # Options: INCREMENTAL, FULL, RECONCILIATION
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
    )

    try:
        operation = client.import_documents(request=request)
        print(f"--- Started GCS import from: {gcs_uri} ---")
        return operation
    except Exception as e:
        print(f"--- Error starting GCS import: {e} ---")


def create_gdrive_datastore(project_id: str, location: str, data_store_id: str):
    """Creates a Google Drive data store."""
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    data_store = discoveryengine.DataStore(
        display_name=f"{data_store_id}-ds",
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
    )

    # Explicitly set the regional endpoint to match the resource location
    client_options = {"api_endpoint": f"{location}-discoveryengine.googleapis.com"}
    client = discoveryengine.DataStoreServiceClient(client_options=client_options)
    try:
        operation = client.create_data_store(
            parent=parent,
            data_store=data_store,
            data_store_id=data_store_id,
        )
        print(f"--- Waiting for GDrive datastore to create: {data_store_id} ---")
        response = operation.result()
        print(f"--- GDrive datastore created: {response.name} ---")
        return response
    except exceptions.AlreadyExists:
        print(f"--- GDrive datastore {data_store_id} already exists. ---")
        return client.get_data_store(name=f"{parent}/dataStores/{data_store_id}")


def create_gmail_datastore(project_id: str, location: str, data_store_id: str):
    """Creates a GMail data store."""
    # Note: As of late 2023, direct GMail data store creation via API is not
    # officially documented. This is a potential implementation based on
    # expected future support.
    # You might need to create it manually in the Google Cloud Console.
    print("--- GMail datastore creation is not yet supported via this script ---")
    print("--- Please create it manually in the Google Cloud Console ---")


if __name__ == "__main__":
    load_dotenv()
    project_id = os.environ.get("PROJECT_ID")
    if not project_id:
        raise ValueError("PROJECT_ID environment variable not set.")

    location = os.environ.get("LOCATION")
    if not location:
        raise ValueError("LOCATION environment variable not set.")

    # Generate a random suffix to ensure data store IDs are unique
    random_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))

    bucket_name = f"{project_id}-bucket"
    gcs_data_store_id = f"gcs-datastore-{random_suffix}"
    gdrive_data_store_id = f"gdrive-datastore-{random_suffix}"
    gmail_data_store_id = "gmail-datastore"

    # GCS bucket locations can be regions or multi-regions. The LOCATION variable
    # from config.sh is 'us', which is a multi-region, so we can use it directly.
    # It's conventionally uppercase for buckets.
    create_gcs_bucket(project_id, bucket_name, location.upper())
    
    # Upload sample files to the bucket
    upload_sample_files(bucket_name)

    # Create the GCS data store and then import data from the bucket
    gcs_datastore_response = create_gcs_datastore(project_id, location, gcs_data_store_id)
    if gcs_datastore_response:
        import_from_gcs(project_id, location, gcs_data_store_id, bucket_name)

    create_gdrive_datastore(project_id, location, gdrive_data_store_id)
    create_gmail_datastore(project_id, location, gmail_data_store_id)

    print("\n--- All data stores created (or skipped) ---")
    print(f"GCS Bucket: {bucket_name}")
    print(f"GCS Data Store ID: {gcs_data_store_id}")
    print(f"GDrive Data Store ID: {gdrive_data_store_id}")
    print(f"GMail Data Store ID: {gmail_data_store_id} (manual creation needed)")

    # Write the generated data store IDs to a .tfvars file for Terraform to use
    with open("datastores.auto.tfvars", "w") as f:
        f.write(f'gcs_data_store_id = "{gcs_data_store_id}"\n')
        f.write(f'gdrive_data_store_id = "{gdrive_data_store_id}"\n')
    print("\n--- Terraform variable file 'datastores.auto.tfvars' created. ---")

    print("\n--- Manual Step: Configure Identity Provider (IdP) ---")
    print("To set up the Identity Provider for your Gemini Enterprise app (required for Google Drive and Gmail data stores):")
    print(f"1. Go to: https://console.cloud.google.com/gemini-enterprise/locations/{location}/engines/YOUR_ENGINE_ID/overview/identity?orgonly=true&walkthrough_id=gemini-enterprise--identity-v1--create--quickstart")
    print("2. Replace 'YOUR_ENGINE_ID' in the URL with the actual engine ID from 'terraform apply' output.")
    print("3. Follow the on-screen instructions to configure the IdP.")