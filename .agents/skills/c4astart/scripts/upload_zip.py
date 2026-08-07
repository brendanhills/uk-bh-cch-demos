#!/usr/bin/env python3
"""This module provides a CLI tool to upload ZIP files to the prototype service."""

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import uuid
import zipfile

ENDPOINT = "https://start.c4a.corp.goog/api/v1/applications"
DEV_ENDPOINT = "https://start.c4a-test.corp.goog/api/v1/applications"


def get_source_type(file_path: pathlib.Path) -> str:
  """Determines the source type based on ZIP contents."""
  try:
    with zipfile.ZipFile(file_path, "r") as z:
      namelist = z.namelist()
      has_package_json = "package.json" in namelist
      has_index_html = "index.html" in namelist

      if not has_package_json and has_index_html:
        return "STATIC_WEBSITE_ZIP"
  except zipfile.BadZipFile:
    print(f"Error: '{file_path}' is not a valid ZIP file.")
    sys.exit(1)
  return "ZIP"


def prepare_multipart_data(
    file_path: pathlib.Path,
    repo_name: str,
    application_name: str,
    source_type: str,
    out_file,
) -> str:
  """Prepares and writes the multipart data for upload to out_file."""
  boundary = uuid.uuid4().hex

  def write_field(name, value):
    out_file.write(f"--{boundary}\r\n".encode("utf-8"))
    out_file.write(
        f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8")
    )
    out_file.write(f"{value}\r\n".encode("utf-8"))

  def write_file_meta(name, filename, content_type):
    out_file.write(f"--{boundary}\r\n".encode("utf-8"))
    if filename:
      out_file.write(
          f'Content-Disposition: form-data; name="{name}";'
          f' filename="{filename}"\r\n'.encode("utf-8")
      )
    else:
      out_file.write(
          f'Content-Disposition: form-data; name="{name}"\r\n'.encode("utf-8")
      )
    out_file.write(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))

  write_field("name", application_name)
  write_field("description", "")
  write_field("sourceType", source_type)

  components_json = json.dumps(
      [{"name": application_name, "githubRepoName": repo_name}]
  )
  write_file_meta("components", None, "application/json")
  out_file.write(components_json.encode("utf-8"))
  out_file.write(b"\r\n")

  write_file_meta("file", file_path.name, "application/zip")
  with open(file_path, "rb") as f:
    chunk_size = 1024 * 1024  # 1MB chunks
    while True:
      chunk = f.read(chunk_size)
      if not chunk:
        break
      out_file.write(chunk)
  out_file.write(b"\r\n")

  out_file.write(f"--{boundary}--\r\n".encode("utf-8"))

  return f"multipart/form-data; boundary={boundary}"


def upload_zip(
    file_path: pathlib.Path,
    c4a_path: str,
    repo_name: str,
    application_name: str,
) -> int:
  """Uploads a ZIP file to the specified endpoint using gosso."""
  if not file_path.exists():
    print(f"Error: File '{file_path}' does not exist.")
    sys.exit(1)

  if file_path.suffix.lower() != ".zip":
    print(f"Error: File '{file_path}' is not a ZIP file.")
    sys.exit(1)

  source_type = get_source_type(file_path)

  tmp_path = None
  try:
    # Use a temporary file to store the multipart data because binary data (ZIP)
    # cannot be passed safely as a string argument via the --data flag.
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
      tmp_path = tmp.name
      content_type = prepare_multipart_data(
          file_path, repo_name, application_name, source_type, tmp
      )
  except OSError as e:
    print(f"Failed to prepare upload data: {e}")
    sys.exit(1)

  print(f"Uploading '{file_path}' for repo '{repo_name}' to {c4a_path}...")

  cmd = [
      "/google/bin/releases/gosso/gosso",
      f"--url={c4a_path}",
      f"--data_file={tmp_path}",
      "--method=POST",
      f"--header=Content-Type: {content_type}",
  ]

  try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
  except FileNotFoundError:
    print("Error: 'gosso' tool not found. Please ensure it is installed.")
    sys.exit(1)
  except subprocess.SubprocessError as e:
    print(f"An error occurred during the upload process: {e}")
    sys.exit(1)
  finally:
    # Clean up the temporary file
    if tmp_path and os.path.exists(tmp_path):
      os.unlink(tmp_path)

  if result.returncode == 0:
    print("Successfully uploaded ZIP file.")
    print(f"Response: {result.stdout}")
    try:
      response_data = json.loads(result.stdout)
      return int(response_data["id"])
    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
      print(f"Error parsing application ID from response: {e}")
      sys.exit(1)
  else:
    print(f"Failed to upload ZIP file. Return code: {result.returncode}")
    print(f"Error: {result.stderr}")
    print(f"Response: {result.stdout}")
    sys.exit(1)


def main():
  """Main entry point for the upload script."""
  parser = argparse.ArgumentParser(
      description="Upload a ZIP file to the prototype service."
  )
  parser.add_argument(
      "file_path", type=str, help="Path to the ZIP file to upload"
  )
  parser.add_argument(
      "--repo-name", type=str, required=True, help="Name of the repository"
  )
  parser.add_argument(
      "--application-name",
      type=str,
      required=True,
      help="Name of the application",
  )
  parser.add_argument(
      "--test-env", action="store_true", help="Use dev instance of C4A starter"
  )

  args = parser.parse_args()
  file_path = pathlib.Path(args.file_path)

  path: str = DEV_ENDPOINT if args.test_env else ENDPOINT
  upload_zip(file_path, path, args.repo_name, args.application_name)


if __name__ == "__main__":
  main()
