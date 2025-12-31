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

### 3. Deploy Infrastructure with Terraform

Use Terraform to deploy the core infrastructure, including the Discovery Engine search engine.

```bash
# Initialize Terraform (only needs to be run once)
terraform init

# Apply the Terraform configuration
terraform apply --auto-approve
```

### 4. Install Python Dependencies & Setup GE Data Stores etc

Run the following commands to install Python packages and then run the script that sets up Gemini Enterprise. This script creates the GCS bucket and associated data stores.

```bash
# Install dependencies
uv sync

# Run the ge_setup script
uv run ge_setup.py
```

**Note on GMail Data Store**: Direct GMail data store creation is not yet supported via the API and needs to be done manually in the Google Cloud Console.

After completing these steps, your core infrastructure and data stores will be set up.
