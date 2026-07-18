import pytest
import os
import json
from unittest.mock import patch, MagicMock

# Import the download_from_gcs function from import_glossary.
# Note: This may initially fail to import, or if it succeeds, it must fail because the feature isn't implemented.
try:
    from import_glossary import download_from_gcs
except ImportError:
    download_from_gcs = None

def test_download_from_gcs_missing_implementation():
    """Verify that if download_from_gcs is missing or raises an error initially (Red Phase)."""
    assert download_from_gcs is not None, "download_from_gcs must be defined in import_glossary.py"

@patch("import_glossary.storage.Client")
def test_download_from_gcs_success(mock_storage_client, tmp_path):
    """Test successful GCS sync download for both JSON and CSV files."""
    # Setup paths under tmp_path
    local_json = str(tmp_path / "glossary.json")
    local_csv = str(tmp_path / "glossary.csv")
    
    # Mock storage classes
    mock_client = MagicMock()
    mock_storage_client.return_value = mock_client
    mock_bucket = MagicMock()
    mock_client.bucket.return_value = mock_bucket
    
    mock_blob_json = MagicMock()
    mock_blob_csv = MagicMock()
    mock_bucket.blob.side_effect = lambda path: mock_blob_json if "json" in path else mock_blob_csv
    
    # Run download_from_gcs
    gcs_csv_uri = "gs://my-bucket/path/glossary.csv"
    download_from_gcs(
        gcs_csv_uri=gcs_csv_uri,
        local_json_path=local_json,
        local_csv_path=local_csv
    )
    
    # Assert client calls
    mock_client.bucket.assert_called_once_with("my-bucket")
    mock_bucket.blob.assert_any_call("path/glossary.csv")
    mock_bucket.blob.assert_any_call("path/glossary.json")
    
    mock_blob_csv.download_to_filename.assert_called_once_with(local_csv)
    mock_blob_json.download_to_filename.assert_called_once_with(local_json)

@patch("import_glossary.storage.Client")
def test_download_from_gcs_failure_handling(mock_storage_client):
    """Test that download_from_gcs fails gracefully when GCS download encounters exceptions."""
    mock_client = MagicMock()
    mock_storage_client.return_value = mock_client
    mock_client.bucket.side_effect = Exception("Google Cloud Storage Connection Failed")
    
    # This should not crash, it should raise or print clear developer feedback
    with pytest.raises(Exception) as exc_info:
        download_from_gcs(
            gcs_csv_uri="gs://my-bucket/glossary.csv",
            local_json_path="glossary/glossary.json",
            local_csv_path="glossary/glossary.csv"
        )
    assert "Google Cloud Storage Connection Failed" in str(exc_info.value)
