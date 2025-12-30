import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1 as discoveryengine


def create_data_store(
    project_id: str, location: str, data_store_id: str, display_name: str
) -> discoveryengine.DataStore:
    """Creates a Discovery Engine data store."""
    client = discoveryengine.DataStoreServiceClient()
    parent = client.collection_path(
        project=project_id, location=location, collection="default_collection"
    )

    data_store = discoveryengine.DataStore(
        display_name=display_name,
        industry_vertical="GENERIC",
        solution_types=["SOLUTION_TYPE_SEARCH"],
        content_config=discoveryengine.DataStore.ContentConfig.UNSTRUCTURED,
    )

    print(f"Creating data store: {data_store_id}...")
    operation = client.create_data_store(
        request=discoveryengine.CreateDataStoreRequest(
            parent=parent,
            data_store=data_store,
            data_store_id=data_store_id,
        )
    )
    response = operation.result()
    print(f"Data store created: {response.name}")
    return response


def import_from_gcs(
    project_id: str, location: str, data_store_id: str, gcs_bucket_name: str
):
    """Imports documents from a GCS bucket into a data store."""
    client = discoveryengine.DocumentServiceClient()
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

    print(f"Starting import from {gcs_uri}...")
    operation = client.import_documents(request=request)
    response = operation.result()
    print(f"Import finished: {response}")
    print(f"Number of successful imports: {response.success_count}")
    print(f"Number of failed imports: {response.failure_count}")


if __name__ == "__main__":
    load_dotenv()

    project_id = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION")
    data_store_id = os.getenv("DATA_STORE_ID")
    bucket_name = os.getenv("BUCKET_NAME")
    data_store_display_name = os.getenv("DATA_STORE_DISPLAY_NAME", "My GCS Data Store")

    if not all([project_id, location, data_store_id, bucket_name]):
        raise ValueError("Please ensure PROJECT_ID, LOCATION, DATA_STORE_ID, and BUCKET_NAME are set in your .env file.")

    # 1. Create the Data Store
    data_store = create_data_store(
        project_id=project_id,
        location=location,
        data_store_id=data_store_id,
        display_name=data_store_display_name,
    )

    # 2. Import documents from GCS into the new data store
    import_from_gcs(
        project_id=project_id,
        location=location,
        data_store_id=data_store.data_store_id,
        gcs_bucket_name=bucket_name,
    )
