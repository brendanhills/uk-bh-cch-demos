# C4A Starter Upload Guide

This guide describes how to use the `upload_zip.py` script to upload application
prototypes (ZIP files) to the C4A Starter service.

## Script Usage

The `upload_zip.py` script packages a ZIP file with metadata and uploads it via
the `gosso` tool. You can find this script by cloning the GHES repository
(`https://depot.code.corp.goog/fog-idp/porcupette-cli`) or by referring to the
native Piper fallback at
`google3/coresystems/developer/coe/idp/skills/c4astart/scripts/upload_zip.py`.

### Command Syntax

```bash
python3 upload_zip.py <path/to/zip_file> --repo-name <repo_name> --application-name <app_name> [--test-env]
```

### Parameters

-   `file_path`: Path to the ZIP file to upload.
-   `--repo-name`: Name of the repository associated with the prototype.
-   `--application-name`: Name of the application.
-   `--test-env` (optional): Use the dev instance of the C4A starter.

## Workflows

### 1. Uploading a Git Repository

To upload a Git repository, you must first create a ZIP archive of the
repository content (excluding the `.git` directory if desired).

```bash
# Create a ZIP of the current directory, excluding .git
zip -r prototype.zip . -x "*.git*"

# Upload using the script
python3 upload_zip.py prototype.zip --repo-name my-repo --application-name my-app
```

### 2. Uploading Static Files

For static files (e.g., a simple HTML/JS app), ZIP the directory containing the
files.

```bash
# ZIP the 'dist' directory
zip -r static_app.zip dist/

# Upload using the script
python3 upload_zip.py static_app.zip --repo-name my-static-repo --application-name my-static-app
```

## Requirements

-   **Python 3**: The script must be run with `python3`.
-   **Dependencies**: `requests` library must be installed.
-   **gosso**: The `gosso` tool must be installed and available in the `PATH`.
-   **Authentication**: `gosso` handles authentication internally.

## Common Issues

-   **Missing ZIP**: Ensure the file you are uploading has a `.zip` extension.
-   **gosso Not Found**: If `gosso` is missing, install it via `sudo apt install
    gosso`.
-   **Binary Data**: ZIP files are binary; the script uses a temporary file and
    `gosso --data_file` to ensure binary safety.
-   **Blank Page or Deployment Failure**: C4A Starter uses Cloud Run. If your
    application exposes a port other than `8080` (like `3000`), the deployment
    will fail to render. Ensure your application listens on port 8080.
