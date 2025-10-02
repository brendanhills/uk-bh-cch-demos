 # 🤖 Gemini CAD Drawing Analyzer
 
 This Streamlit web application uses Google's Gemini 2.5 Flash multimodal model via Vertex AI to analyze technical CAD drawings. Users can select a drawing from a Google Cloud Storage (GCS) bucket, provide custom instructions and prompts, and receive a detailed analysis. The complete report, including the image, prompts, and Gemini's response, can be saved directly to a Google Doc.
 
 ## ✨ Features
 
 - **Web-based UI:** Simple and interactive interface built with Streamlit.
 - **GCS Integration:** Browse and select image files directly from a specified GCS bucket.
 - **Powerful Multimodal AI:** Utilizes the `gemini-2.5-flash` model for fast and capable image analysis.
 - **Customizable Analysis:** Tailor the AI's output with custom system instructions and user prompts.
 - **Streaming Responses:** View the AI's analysis as it's being generated in real-time.
 - **Export to Google Docs:** Save a complete, formatted report of the analysis—including the image, prompts, and AI response—to Google Docs using service account impersonation for secure access.
 
 ## 🛠️ Tech Stack & Architecture
 
 - **Frontend:** Streamlit
 - **AI Model:** Google Vertex AI (Gemini 2.5 Flash)
 - **Cloud Storage:** Google Cloud Storage (GCS)
 - **Document Export:** Google Docs API & Google Drive API
 - **Authentication:** Google Cloud Application Default Credentials (ADC) & Service Account Impersonation.
 - **Dependency Management:** uv
 
 ## 📋 Prerequisites
 
 Before you begin, ensure you have the following:
 
 1.  **Google Cloud Project:** A GCP project with billing enabled.
 2.  **Enabled APIs:** In your GCP project, enable the following APIs:
     - Vertex AI API
     - Google Drive API
     - Google Docs API
 3.  **Google Cloud Storage Bucket:** A GCS bucket containing the CAD drawing images you want to analyze.
 4.  **Service Accounts & IAM Permissions:**
     - **App Service Account (SA-App):** The service account that runs the Streamlit application (e.g., on Cloud Run). This SA needs:
         - `Vertex AI User` role (to call the Gemini model).
         - `Storage Object Viewer` role (to read images from the GCS bucket).
         - `Service Account Token Creator` role **on the Docs Service Account (SA-Docs)**.
     - **Docs Service Account (SA-Docs):** A dedicated service account to be impersonated for creating documents. This SA needs:
         - `Google Docs API User` (or a custom role with `document.create` permissions).
         - `Drive Filer` or `Editor` role on the Google Drive folder where documents will be saved.
 5.  **Python & `uv`:** Python 3.11+ and `uv` installed on your local machine.
 
 ## 🚀 Setup & Installation
 
 1.  **Clone the Repository:**
     ```bash
     git clone <your-repository-url>
     cd cad_analyser
     ```
 
 2.  **Install UV**: (if you don't have it already)
        This project uses `pyproject.toml` to manage dependencies. The fastest way to install them is with `uv`.
      ```bash
      pip install uv
      ```
      or
      ```bash
      pipx install uv
      ```
        See other install options here:  https://docs.astral.sh/uv/getting-started/installation/

 
 3.  **Install Dependencies with `uv`:**
     Use `uv` to sync your virtual environment with the specified packages. This is the fastest way to create a .venv and install dependencies.
     ```bash
     uv sync
     ```
 
 4.  **Local Authentication:**
     For local development, authenticate your user account with Google Cloud. This allows the application to use your credentials.
     ```bash
     gcloud auth application-default login
     ```
 
 ## ⚙️ Configuration
 
 The application is configured using a `secrets.toml` file located in the `.streamlit` directory.
 
 1.  Create the directory and file:
     ```bash
     mkdir .streamlit
     touch .streamlit/secrets.toml
     ```
 
 2.  Add your configuration details to `secrets.toml`. **Do not commit this file to version control.**
 
     ```toml
     # .streamlit/secrets.toml
 
     [gcp]
     project_id = "your-gcp-project-id"
     location = "your-gcp-region" # e.g., "us-central1"
     bucket_name = "gs://your-gcs-bucket-name/path/to/images"
 
     [google_docs_api]
     # The email of the service account to impersonate for creating Google Docs.
     target_service_account_email = "sa-docs-account@your-gcp-project-id.iam.gserviceaccount.com"
 
     [app]
     default_system_instruction = "You are an expert mechanical engineer. Your task is to analyze the provided CAD drawing and provide a detailed, structured technical summary. Focus on materials, dimensions, tolerances, and potential manufacturing processes. Use markdown for formatting."
     default_prompt = "Please provide a comprehensive analysis of the attached drawing. Identify the main components, list all specified dimensions and tolerances, and suggest a suitable manufacturing method for this part."
     ```
 
 ## ▶️ Running the Application
 
 Once the setup and configuration are complete, run the Streamlit app from your terminal:
 
 ```bash
 streamlit run cad_analayser_app.py
 ```
 
 The application will open in your default web browser.
 
 ## 📖 Usage
 
 1.  The app will load and display a list of images from your configured GCS bucket in the dropdown menu.
 2.  Select an image to analyze. It will be displayed on the screen.
 3.  Review or modify the **System Instructions** and **Analysis Prompt** in the text areas.
 4.  Click the **🚀 Analyze Image** button.
 5.  The AI's response will stream into the "Diagram Analysis" section.
 6.  Once the analysis is complete, a **💾 Save to Google Doc** button will appear. Click it to generate a Google Doc containing the image, prompts, and full response. A link to the new document will be provided.
