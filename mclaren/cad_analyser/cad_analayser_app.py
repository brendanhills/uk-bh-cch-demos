from google.genai import types
from google.genai.types import Part
import streamlit as st
from google.cloud import storage
from google import genai
from PIL import Image
import io
import os
from dotenv import load_dotenv
import vertexai
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import google.auth
from google.auth.impersonated_credentials import Credentials

# Load environment variables from .env file
load_dotenv()

# Google API client imports for Docs and Drive


# Imports for service account impersonation


# --- Configuration & Page Setup ---
st.set_page_config(
    page_title="Gemini CAD Drawing Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- Helper Functions ---

# Function to list GCS buckets
@st.cache_data(ttl=600)
def list_gcs_buckets(project):
    """Lists all available GCS buckets for the project."""
    try:
        storage_client = storage.Client(project)
        buckets = [bucket.name for bucket in storage_client.list_buckets()]
        return buckets
    except Exception as e:
        st.error("Failed to list GCS buckets.")
        st.error(f"Error: {e}")
        st.info("Please ensure you have authenticated correctly with GCP.")
        return []

# Function to list image files in a GCS bucket
@st.cache_data(ttl=600)  # Cache the file list for 10 minutes
def list_gcs_images(gs_path):
    """Lists all image files in a given GCS bucket."""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    try:
        storage_client = storage.Client()
        bucket_name, image_path = get_bucket_and_path(gs_path)
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=image_path)
        image_files = [blob.name for blob in blobs if any(blob.name.lower().endswith(ext) for ext in image_extensions)]
        return image_files
    except Exception as e:
        st.error(f"Failed to connect to GCS bucket '{gs_path}'.")
        st.error(f"Error: {e}")
        st.info("Please ensure your bucket_name in .streamlit/secrets.toml is correct.")
        st.info("For local development, run 'gcloud auth application-default login' in your terminal.")
        return []

# Function to get an image from GCS
@st.cache_data(ttl=600)
def get_gcs_image(gs_path, file_name):
    """Downloads an image from GCS and returns it as a PIL Image."""
    try:
        bucket_name, image_path = get_bucket_and_path(gs_path)
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        image_bytes = blob.download_as_bytes()
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Failed to load image '{file_name}' from bucket.")
        st.error(f"Error: {e}")
        return None

def get_bucket_and_path(gs_path):
    parts = gs_path.split("/", 3)
    bucket_name = parts[2]
    image_path = parts[3] if len(parts) > 3 else ""
    return bucket_name, image_path

# Function to call Vertex AI Gemini API
def analyze_image_with_vertex_gemini(image, system_instruction, prompt):
    """Analyzes an image using the Vertex AI Gemini 2.5 Flash model."""
    try:
        model = "gemini-2.5-flash"

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        genai_client = genai.Client(
            vertexai=True,
            project = gcp_project_id,
            location = gcp_location
        )

        prompt_1 = types.Part.from_text(text=prompt)

        cad_image1 = Part.from_bytes(
            data=image_bytes,
            mime_type="image/png"
        )

        contents = types.Content(
                role="user",
                parts=[
                    cad_image1,
                    prompt_1
                ]
            )

        tools = [
            types.Tool(google_search=types.GoogleSearch()),
        ]

        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 1,
            seed = 0,
            max_output_tokens = 65535,
            safety_settings = [types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            ),types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_NONE
            )],
            tools = tools,
            system_instruction=system_instruction,
            thinking_config=types.ThinkingConfig(
            thinking_budget=-1,
            ),
        )

        response = genai_client.models.generate_content(
            model = model,
            contents = contents,
            config = generate_content_config,
        )
        return response, generate_content_config
    except Exception as e:
        st.error(f"An error occurred with the Vertex AI Gemini API.")
        st.error(f"Error: {e}")
        st.info("Please ensure your project_id and location in .streamlit/secrets.toml are correct, and that the Vertex AI API is enabled in your project.")
        return None, None

# Function to create a Google Doc with analysis results
def create_google_doc(
    image_pil: Image.Image,
    system_instruction: str,
    prompt: str,
    gemini_response: str,
    gemini_config: types.GenerateContentConfig,
    target_service_account_email: str # New parameter for the service account to impersonate
):
    """
    Creates a Google Doc with the analysis results using service account impersonation.
    Uploads image to Google Drive, then inserts into Google Doc.
    """
    try:
        # Setup Google Docs and Drive API scopes
        SCOPES = ['https://www.googleapis.com/auth/documents',
                  'https://www.googleapis.com/auth/drive.file']

        # Get default credentials (from environment or gcloud auth)
        # These will be the credentials of the service account running the Streamlit app
        credentials, project = google.auth.default()

        # Create impersonated credentials
        # The service account running this app needs 'Service Account Token Creator' role
        # on the target_service_account_email
        impersonated_creds = Credentials(
            source_credentials=credentials,
            target_principal=target_service_account_email,
            target_scopes=SCOPES,
            lifetime=600 # 10 minutes lifetime for impersonated token
        )

        docs_service = build('docs', 'v1', credentials=impersonated_creds)
        drive_service = build('drive', 'v3', credentials=impersonated_creds)

        # 1. Create a new Google Doc
        title = f"CAD Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        document = docs_service.documents().create(body={'title': title}).execute()
        document_id = document.get('documentId')
        st.success(f"Google Doc created: [Link to Document](https://docs.google.com/document/d/{document_id}/edit)")

        requests = []

        # All insertions will be at index 1 to push content down, achieving desired order:
        # Image
        # System Instructions
        # Prompt
        # Gemini Parameters
        # Gemini Response

        # 2. Insert Gemini Response
        requests.append({
            'insertText': {
                'text': f"\n\n**Gemini Response:**\n{gemini_response}\n\n",
                'endIndex': 1,
            }
        })

        # 3. Insert Gemini Parameters
        params_text = "**Gemini Parameters:**\n"
        if gemini_config:
            if gemini_config.temperature is not None:
                params_text += f"- Temperature: {gemini_config.temperature}\n"
            if gemini_config.top_p is not None:
                params_text += f"- Top P: {gemini_config.top_p}\n"
            if gemini_config.seed is not None:
                params_text += f"- Seed: {gemini_config.seed}\n"
            if gemini_config.max_output_tokens is not None:
                params_text += f"- Max Output Tokens: {gemini_config.max_output_tokens}\n"
        else:
            params_text += "- No specific Gemini parameters captured.\n"
        requests.append({
            'insertText': {
                'text': params_text + "\n",
                'endIndex': 1,
            }
        })

        # 4. Insert Prompt
        requests.append({
            'insertText': {
                'text': "**Prompt:**\n" + prompt + "\n\n",
                'endIndex': 1,
            }
        })

        # 5. Insert System Instruction
        requests.append({
            'insertText': {
                'text': "**System Instructions:**\n" + system_instruction + "\n\n",
                'endIndex': 1,
            }
        })

        # 6. Upload Image to Google Drive
        img_byte_arr = io.BytesIO()
        image_pil.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0) # Rewind to beginning of file

        image_filename = f'CAD_Image_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        file_metadata = {
            'name': image_filename,
            'mimeType': 'image/png',
            # For a service account, files are owned by the service account.
            # If you need users to easily find this, consider storing it in a shared folder
            # to which the service account has access and the user is a member.
        }
        media = MediaIoBaseUpload(img_byte_arr, mimetype='image/png', resumable=True)
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webContentLink, webViewLink' # Request webContentLink for embedding
        ).execute()
        image_file_id = uploaded_file.get('id')
        image_content_link = uploaded_file.get('webContentLink') # This is the direct link for embedding

        st.info(f"Image uploaded to Google Drive with ID: `{image_file_id}`.")

        if image_content_link:
            # Get original image dimensions for proportional scaling
            width, height = image_pil.size
            # Calculate new width and height to fit within a reasonable document size (e.g., max 600px width)
            max_width_pt = 450 # Approx 6 inches at 72 dpi (Google Docs uses points)
            if width > max_width_pt:
                scale_factor = max_width_pt / width
                new_width = max_width_pt
                new_height = height * scale_factor
            else:
                new_width = width
                new_height = height

            # Insert image at the very beginning of the document
            requests.append({
                'insertInlineImage': {
                    'uri': image_content_link,
                    'objectProperties': {
                        'imageProperties': {
                            'contentUri': image_content_link,
                            'width': { 'magnitude': new_width, 'unit': 'PT' },
                            'height': { 'magnitude': new_height, 'unit': 'PT' }
                        }
                    },
                    'endIndex': 1 # Always insert at the beginning, pushing existing content down
                }
            })
            requests.append({
                'insertText': {
                    'text': "\n\n", # Add some spacing after the image
                    'endIndex': 1,
                }
            })
        else:
            st.warning("Could not get a direct content link for the image. Image may not display in the document.")
            requests.append({
                'insertText': {
                    'text': f"Image Placeholder (could not embed directly). View on Drive: https://drive.google.com/file/d/{image_file_id}/view\n\n",
                    'endIndex': 1,
                }
            })

        # Execute all batch updates
        docs_service.documents().batchUpdate(
            documentId=document_id, body={'requests': requests}
        ).execute()

        st.success(f"Content successfully added to Google Doc '{title}'.")

    except Exception as e:
        st.error(f"Failed to create Google Doc: {e}")
        st.info("Please ensure the Google Docs API and Google Drive API are enabled for your GCP project, and the service account running this app has the 'Service Account Token Creator' role on the target service account being impersonated, and the target service account has permissions to create/edit Drive files.")


# --- Streamlit UI ---

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Load configuration from environment variables or secrets file
    gcp_project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or st.secrets.get("gcp", {}).get("project_id")
    gcp_location = os.environ.get("GOOGLE_CLOUD_LOCATION") or st.secrets.get("gcp", {}).get("location")
    gcs_bucket_from_secrets = st.secrets.get("gcp", {}).get("bucket_name")
    gcs_folder_from_secrets = st.secrets.get("gcp", {}).get("folder_name")
    default_prompt = st.secrets.get("app", {}).get("default_prompt")
    default_system_instruction = st.secrets.get("app", {}).get("default_system_instruction")

    # Load Google Docs impersonation target service account email
    google_docs_service_account_email = st.secrets.get("google_docs_api", {}).get("target_service_account_email")

    # Display loaded configuration
    st.write(f"**Project ID:** `{gcp_project_id}`")
    st.write(f"**Location:** `{gcp_location}`")
    
    available_buckets = list_gcs_buckets(gcp_project_id)
    
    if available_buckets:
        bucket_name_from_secrets = ""
        if gcs_bucket_from_secrets:
            if gcs_bucket_from_secrets.startswith("gs://"):
                bucket_name_from_secrets = gcs_bucket_from_secrets.split('/')[2]
            else:
                # Assume it's either 'bucket-name' or 'bucket-name/folder'
                bucket_name_from_secrets = gcs_bucket_from_secrets.split('/')[0]

        default_index = 0
        if bucket_name_from_secrets in available_buckets:
            default_index = available_buckets.index(bucket_name_from_secrets)

        selected_bucket = st.selectbox(
            "Select GCS Bucket:",
            options=available_buckets,
            index=default_index
        )

        folder_name = gcs_folder_from_secrets
        folder_path = st.text_input(
            "Optional: Folder path within bucket (e.g., 'cad_drawings/project_x')",
            folder_name
        )
        
        if folder_path:
            gcs_bucket_name = f"gs://{selected_bucket}/{folder_path}"
        else:
            gcs_bucket_name = f"gs://{selected_bucket}"
            
        st.write(f"**Selected GCS Path:** `{gcs_bucket_name}`")
    else:
        st.warning("Could not list any GCS buckets. Please check your GCP project configuration and permissions.")
        gcs_bucket_name = st.text_input(
            "GCS Bucket Name:",
            value=gcs_bucket_from_secrets,
            placeholder="e.g. my-cad-bucket/folder"
        )
        st.write(f"**Bucket Name:** `{gcs_bucket_name}`")


st.title("🤖 Gemini CAD Drawing Analyzer")
st.markdown("Select a CAD Drawing from your GCS bucket, provide a prompt, and let Gemini generate a detailed technical analysis.")

# Initialize session state variables to hold results across reruns
if "full_response_text" not in st.session_state:
    st.session_state.full_response_text = None
if "gemini_config" not in st.session_state:
    st.session_state.gemini_config = None
if "analysis_inputs" not in st.session_state:
    st.session_state.analysis_inputs = None

# --- Main App Logic ---
if gcp_project_id and gcp_location and gcs_bucket_name:
    # --- Vertex AI Initialization ---
    try:
        vertexai.init(project=gcp_project_id, location=gcp_location)
        st.sidebar.success(f"Vertex AI Initialized for project '{gcp_project_id}'")
        initialized = True
    except Exception as e:
        st.sidebar.error(f"Failed to initialize Vertex AI.")
        st.sidebar.error(f"Error: {e}")
        initialized = False
        st.stop()
    
    image_files = list_gcs_images(gcs_bucket_name)
    
    if image_files:
        # --- Image Selection ---
        selected_image_file = st.selectbox(
            "Select an image from the bucket:",
            options=image_files,
            index=0
        )
        
        if selected_image_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🖼️ Selected Image")
                with st.spinner("Loading image from GCS..."):
                    image = get_gcs_image(gcs_bucket_name, selected_image_file)
                    if image:
                        st.image(image, caption=f"Image: {selected_image_file}", width='stretch')

            with col2:
                st.subheader("📝 System Instruction")
                system_instruction = st.text_area(
                    "System Instructions:",
                    height=200,
                    value=default_system_instruction
                )

                st.subheader("📝 Analysis Prompt")
                prompt = st.text_area(
                    "CAD Analysis prompt:",
                    height=300,
                    value=default_prompt
                )

                analyze_button = st.button("🚀 Analyze Image", type="primary", width='stretch')

            # --- Analysis Execution ---
            if analyze_button:
                # Reset previous results when starting a new analysis
                st.session_state.full_response_text = None
                st.session_state.gemini_config = None
                st.session_state.analysis_inputs = None

                if not prompt:
                    st.warning("Please enter an analysis prompt.")
                elif image and initialized:
                    with st.spinner("Gemini is analyzing the image... This may take a moment."):
                        analysis_stream, gemini_config = analyze_image_with_vertex_gemini(image, system_instruction, prompt)

                    st.divider()
                    st.subheader("📄 Diagram Analysis:")
                    if analysis_stream:
                        # Store inputs for the save button to ensure consistency
                        st.session_state.analysis_inputs = {
                            "image": image,
                            "system_instruction": system_instruction,
                            "prompt": prompt,
                        }

                        # Directly get the text from the non-streamed response
                        full_response_text = analysis_stream.text
                        st.write(full_response_text)

                        # Once the response is complete, save the full text and config to session state.
                        st.session_state.full_response_text = full_response_text
                        st.session_state.gemini_config = gemini_config
                    else:
                        st.error("The analysis failed. Please check the error messages above.")

            # This block now correctly handles the "Save" button click on a script rerun
            # because the result is persisted in st.session_state.
            if st.session_state.full_response_text:
                if st.button("💾 Save to Google Doc", width='stretch'):
                    if google_docs_service_account_email and st.session_state.analysis_inputs:
                        with st.spinner("Saving to Google Docs..."):
                            create_google_doc(
                                st.session_state.analysis_inputs["image"],
                                st.session_state.analysis_inputs["system_instruction"],
                                st.session_state.analysis_inputs["prompt"],
                                st.session_state.full_response_text,
                                st.session_state.gemini_config, # pyright: ignore[reportArgumentType]
                                google_docs_service_account_email
                            )
                    else:
                        st.error("Google Docs API target service account email not found in .streamlit/secrets.toml. Cannot save to Google Doc.")

    elif gcs_bucket_name:
        st.info(f"No image files found in the bucket '{gcs_bucket_name}'. Please check the bucket name and its contents.")
else:
    st.info("Please create a .streamlit/secrets.toml file with your GCP configuration to begin. See the instructions for the required format.")
