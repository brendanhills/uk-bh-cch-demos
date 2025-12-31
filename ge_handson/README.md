# Gemini Hands-on Project

This project demonstrates how to set up various Google Cloud resources for a Gemini Enterprise application, combining Terraform for core infrastructure and Python scripts for data store management.

## Setup Instructions

Follow these steps to set up your environment and deploy the necessary resources.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Google Cloud SDK**: For `gcloud` CLI commands.
*   **Terraform**: For deploying infrastructure.
*   **Python 3.9+**: For running Python scripts.
*   **uv**: A fast Python package installer and resolver.

### 1. Configure Your Environment

All configuration is managed in a single file.

1.  **Edit `config.sh`**: Open `config.sh` and set your master configuration values, such as `PROJECT_ID`, `REGION`, and `LOCATION`.
2.  **Run the script**: Execute the script to export the variables and generate the necessary `terraform.tfvars` and `.env` files.

    ```bash
    chmod +x config.sh
    ./config.sh
    ```

### 2. Set up Cloud Environment & Permissions

Run the `setup_env.sh` script. This will enable the correct APIs and grant the necessary IAM permissions for your project based on the configuration in `config.sh`.

```bash
./setup_env.sh
```

You can verify the setup at any time by running `./check_env.sh`.

**Important: Manual Configuration Steps**
Some Discovery Engine features, like Identity Provider (IdP) configuration for ACL-enabled connectors (e.g., Google Drive, Gmail), cannot be fully automated and require manual intervention in the Google Cloud Console.

-   **Identity Provider (IdP) for ACL-enabled Connectors:**
    To configure the IdP for your Gemini Enterprise app (required for Google Drive and Gmail data stores), visit the following URL. You will need to replace `LOCATION` with your project's location (from `config.sh`) and `ENGINE_ID` with the ID of your search engine (output from `terraform apply`).

    `https://console.cloud.google.com/gemini-enterprise/locations/LOCATION/engines/ENGINE_ID/overview/identity?orgonly=true&walkthrough_id=gemini-enterprise--identity-v1--create--quickstart`

-   **GMail Data Store**: Direct GMail data store creation is not yet supported via the API and needs to be done manually in the Google Cloud Console.

### 3. Install Python Dependencies

Run the following command to install the required Python packages.

```bash
# Install dependencies
uv sync
```

### 4. Create GCS Bucket and Data Stores

Run the script that creates the GCS bucket and associated data stores. These data stores are required by the search engine that will be created in the next step.

```bash
# Run the datastores script
uv run python datastores.py
```

**Note on GMail Data Store**: Direct GMail data store creation is not yet supported via the API and needs to be done manually in the Google Cloud Console.

### 5. Deploy Infrastructure with Terraform

Use Terraform to deploy the core infrastructure, including the Discovery Engine search engine which will connect to the data stores created in the previous step.

```bash
# Initialize Terraform (only needs to be run once)
terraform init

# Apply the Terraform configuration
terraform apply --auto-approve
```

After completing these steps, your core infrastructure and data stores will be set up.
