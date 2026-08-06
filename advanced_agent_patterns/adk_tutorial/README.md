# ADK Day Trip Planning Agent

A specialized AI agent built with Google's AI Development Kit (ADK) that generates creative and fun day trip plans based on user preferences, location, and budget constraints.

**Please make sure to check [goo.gle/advancedadk](https://goo.gle/advancedadk) to set up this project.**

## Features

- 🎯 **Personalized Planning**: Generates trip suggestions based on user interests and preferences
- 📍 **Location-Aware**: Works with city names, addresses, or GPS coordinates
- 💰 **Budget-Conscious**: Targets moderate budget activities (affordable yet valuable)
- 🔍 **Real-Time Search**: Uses Google Search to find current events and venues
- 📅 **Date-Specific**: Plans activities for specific weekend dates
- 🎨 **Creative Suggestions**: Maximum 3 distinct activities per plan with detailed location information

## Tutorial

For a guided walkthrough of how to set up this project, please refer to the [tutorial](https://goo.gle/advancedadk).

## Prerequisites

- Python 3.8 or higher
- Google Cloud SDK installed and authenticated (`gcloud auth login`)

## Quick Setup

This project uses a setup script to configure the environment automatically. Simply run the script for your operating system.

### For Mac/Linux Users

```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### For Windows Users

```cmd
setup_venv.bat
```

### What the Script Does

The setup script will:

1.  **Check for Python**: Ensures you have Python 3.8 or higher.
2.  **Create a Virtual Environment**: Sets up a dedicated `.adk_env` directory.
3.  **Install Dependencies**: Installs the required Python packages from `requirements.txt`.
4.  **Prompt for Project ID**: Asks for your Google Cloud Project ID.
5.  **Create `.env` File**: Generates a `.env` file in the root directory with the following configuration:

    ```env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=your_project_id
    GOOGLE_CLOUD_LOCATION=us-central1
    ```

## Running the Agent

After the setup is complete:

1.  **Activate the virtual environment**:

    **Mac/Linux:**
    ```bash
    source .adk_env/bin/activate
    ```

    **Windows:**
    ```cmd
    .adk_env\Scripts\activate
    ```

2.  **Run the ADK web interface**:

    ```bash
    adk web
    ```

## Deactivating the Environment

When you're done, you can deactivate the virtual environment:

```bash
deactivate
```