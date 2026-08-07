#!/usr/bin/env python3
"""CLI tool to retrieve application metadata from the prototype service."""

import argparse
import json
import shutil
import subprocess
import sys
from typing import Any

ENDPOINT = "https://start.c4a.corp.goog/api/v1/applications"
DEV_ENDPOINT = "https://start.c4a-test.corp.goog/api/v1/applications"


def get_application(
    application_id: int,
    c4a_path: str,
) -> dict[str, Any]:
  """Retrieves application metadata from the specified endpoint using gosso."""
  url = f"{c4a_path}/{application_id}"
  print(
      "Retrieving application metadata for ID"
      f" '{application_id}' from {url}..."
  )

  gosso_path = shutil.which("gosso") or "/google/bin/releases/gosso/gosso"
  cmd = [
      gosso_path,
      f"--url={url}",
      "--method=GET",
  ]

  try:
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=False, timeout=60
    )
  except FileNotFoundError:
    print(f"Error: '{gosso_path}' not found. Please ensure it is installed.")
    sys.exit(1)
  except subprocess.TimeoutExpired as e:
    print(f"The request timed out: {e}")
    sys.exit(1)
  except subprocess.SubprocessError as e:
    print(f"An error occurred during the request: {e}")
    sys.exit(1)

  if result.returncode == 0:
    try:
      return json.loads(result.stdout)
    except json.JSONDecodeError as e:
      print(f"Error parsing JSON response: {e}")
      print(f"Response: {result.stdout}")
      sys.exit(1)
  else:
    print(f"Failed to retrieve application. Return code: {result.returncode}")
    print(f"Error: {result.stderr}")
    print(f"Response: {result.stdout}")
    sys.exit(1)


def main() -> None:
  """Main entry point for the get script."""
  parser = argparse.ArgumentParser(
      description="Retrieve application metadata from the prototype service."
  )
  parser.add_argument(
      "application_id", type=int, help="The ID of the application to retrieve"
  )
  parser.add_argument(
      "--test-env", action="store_true", help="Use dev instance of C4A starter"
  )

  args = parser.parse_args()
  path: str = DEV_ENDPOINT if args.test_env else ENDPOINT
  app_data = get_application(args.application_id, path)
  print(json.dumps(app_data, indent=2))


if __name__ == "__main__":
  main()
