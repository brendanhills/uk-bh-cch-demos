import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google.cloud import storage
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io, pickle, os


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly",  "https://www.googleapis.com/auth/drive"]

FILENAME = "Screen Recording 2025-06-02 at 10.25.02 PM.mov"

BUCKET = "agents-summit25lon-1"
DRIVE_FOLDER_ID = "1KLFTzpt0-aKOO50NUqvFXMQeM2NotPsF"


def list_files(creds):
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      print("No files found.")
      return
    print("Files:")
    for item in items:
      print(f"{item['name']} ({item['id']})")
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

def get_creds():
    creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
    if os.path.exists("token.json"):
      creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
      with open("token.json", "w") as token:
        token.write(creds.to_json())
    return creds


def copy_gcs_to_gdrive(filename, bucket_name, folder_id, creds):
    """Cloud Function to copy a file from Cloud Storage to Google Drive."""

    blob_path = filename

    # Authenticate with Google Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    # Authenticate with Google Drive API
    drive_service = build('drive', 'v3', credentials=creds) # Replace 'creds' with your credentials

    # Download file from Cloud Storage
    downloaded_file = io.BytesIO()
    blob.download_to_file(downloaded_file)
    downloaded_file.seek(0)

    # Upload file to Google Drive
    file_metadata = {'name': filename, 'parents': [folder_id]} # Replace with your folder ID
    media = MediaIoBaseUpload(downloaded_file, mimetype='application/octet-stream', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f'File {filename} uploaded to Google Drive with ID: {file.get("id")}')

def main():
    creds = get_creds()
    list_files(creds)
    copy_gcs_to_gdrive(FILENAME, BUCKET, DRIVE_FOLDER_ID, creds)



if __name__ == "__main__":
  main()