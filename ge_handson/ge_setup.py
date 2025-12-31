import os
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

def create_gcs_datastore(project_id: str, location: str, data_store_id: str):
    """Creates a GCS data store."""
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"
    data_store = discoveryengine.DataStore(
        display_name=f"{data_store_id}-ds",
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config=discoveryengine.DataStore.ContentConfig.NO_CONTENT,
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

    bucket_name = f"{project_id}-bucket"
    gcs_data_store_id = "gcs-datastore"
    gdrive_data_store_id = "gdrive-datastore"
    gmail_data_store_id = "gmail-datastore"

    # GCS bucket locations can be regions or multi-regions. The LOCATION variable
    # from config.sh is 'us', which is a multi-region, so we can use it directly.
    # It's conventionally uppercase for buckets.
    create_gcs_bucket(project_id, bucket_name, location.upper())
    create_gcs_datastore(project_id, location, gcs_data_store_id)
    create_gdrive_datastore(project_id, location, gdrive_data_store_id)
    create_gmail_datastore(project_id, location, gmail_data_store_id)

    print("\n--- All data stores created (or skipped) ---")
    print(f"GCS Bucket: {bucket_name}")
    print(f"GCS Data Store ID: {gcs_data_store_id}")
    print(f"GDrive Data Store ID: {gdrive_data_store_id}")
    print(f"GMail Data Store ID: {gmail_data_store_id} (manual creation needed)")