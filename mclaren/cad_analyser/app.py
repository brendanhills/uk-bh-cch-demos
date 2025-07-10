from google.genai import types
from google.genai.types import Part
import streamlit as st
from google.cloud import storage
from google import genai
from PIL import Image
import io
import os

import vertexai

# --- Configuration & Page Setup ---
st.set_page_config(
    page_title="Vertex AI Gemini Analyzer",
    page_icon="🤖",
    layout="wide"
)

# --- Helper Functions ---

# Function to list image files in a GCS bucket
@st.cache_data(ttl=600)  # Cache the file list for 10 minutes
def list_gcs_images(gs_path):
    """Lists all image files in a given GCS bucket."""
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    try:
        # Assumes user is authenticated via `gcloud auth application-default login` for local dev
        # or running in a GCP environment (like Cloud Run) with appropriate permissions.
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
    bucket_name = gs_path.split("/",3)[2]
    image_path =  gs_path.split("/",3)[3]
    return bucket_name, image_path

# Function to call Vertex AI Gemini API
def analyze_image_with_vertex_gemini(image, system_instruction, prompt):
    """Analyzes an image using the Vertex AI Gemini 2.5 Flash model."""
    try:
        # Model name for Vertex AI Gemini
        model = "gemini-2.5-flash"

        # Convert PIL Image to bytes for the API
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        client = genai.Client(
            vertexai=True,
            project = gcp_project_id,
            location = gcp_location
        )

        # Create the Part object for the prompt
        prompt_1 = types.Part.from_text(text=prompt)

        # Create the Part object for the image
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

        # Generate content using the model
        response = client.models.generate_content_stream(
            model = model,
            contents = contents,
            config = generate_content_config,
        )
        return response
    except Exception as e:
        st.error(f"An error occurred with the Vertex AI Gemini API.")
        st.error(f"Error: {e}")
        st.info("Please ensure your project_id and location in .streamlit/secrets.toml are correct, and that the Vertex AI API is enabled in your project.")
        return None

# --- Streamlit UI ---

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("Settings are now loaded from the `.streamlit/secrets.toml` file.")
    
    # Load configuration from secrets file
    gcp_project_id = st.secrets.get("gcp", {}).get("project_id")
    gcp_location = st.secrets.get("gcp", {}).get("location")
    gcs_bucket_name = st.secrets.get("gcp", {}).get("bucket_name")

    # Display loaded configuration
    st.write(f"**Project ID:** `{gcp_project_id}`")
    st.write(f"**Location:** `{gcp_location}`")
    st.write(f"**Bucket Name:** `{gcs_bucket_name}`")


st.title("🤖 Gemini Technical Image Analyzer (via Vertex AI)")
st.markdown("Select an image from your GCS bucket, provide a prompt, and let Gemini generate a detailed technical analysis.")

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
                        st.image(image, caption=f"Image: {selected_image_file}", use_container_width=True)

            with col2:
                st.subheader("📝 System Instruction")
                system_instruction = st.text_area(
                    "System Instructions:",
                    height=200,
                    value="""You are an expert in understanding and interpreting CAD diagrams for car parts for an engineering team. 
Provide very clear and factual output that is suitable for an experienced engineer to understand. 
Use normal mechanical engineering terminology. Be meticulous and careful."""
                )

                st.subheader("📝 Analysis Prompt")
                prompt = st.text_area(
                    "CAD Analysis prompt:",
                    height=300,
                    value="""You will be provided with a CAD diagram. 
Your task is to create a checklist for this CAD diagram. An engineer will use the checklist to verify all of the dimensions and tolerances are correct in this diagram.

Follow these steps:

1.  Interpret the CAD diagram:
    *   Carefully analyze the provided CAD diagram.
    *   Interpret any symbols on the diagram using standard conventions for CAD drawings.
2.  Create a checklist:
    *   Produce a list of dimensions and tolerances, grouped by component, and ordered in a logical way.
    *   It is very important that you don't make any errors with the numbers in the diagram.
    *   If you are unsure of any number, then make that very clear.
3.  Output the checklist."""
                )

                analyze_button = st.button("🚀 Analyze Image", type="primary", use_container_width=True)

            # --- Analysis Execution ---
            if analyze_button:
                if not prompt:
                    st.warning("Please enter an analysis prompt.")
                elif image and initialized:
                    with st.spinner("Gemini is analyzing the image... This may take a moment."):
                        analysis_stream = analyze_image_with_vertex_gemini(image, system_instruction, prompt)
                    
                    st.divider()
                    st.subheader("📄 Diagram Analysis:")
                    if analysis_stream:
                        stream_iterator = iter(analysis_stream)
                        first_chunk = None

                        # Display a spinner while waiting for the first chunk
                        try:
                            with st.spinner("Generating analysis... Please wait..."):
                                first_chunk = next(stream_iterator)
                        except StopIteration:
                            # Handle the case where the stream is empty
                            st.warning("The model returned an empty response.")

                        if first_chunk:
                            # Create a new generator that starts with the first chunk's text
                            # and then continues with the text from the rest of the stream.
                            def text_generator():
                                yield first_chunk.text
                                for chunk in stream_iterator:
                                    yield chunk.text
                            
                            # Use st.write_stream with the new generator
                            st.write_stream(text_generator)

                    else:
                        st.error("The analysis failed. Please check the error messages above.")
    elif gcs_bucket_name:
        st.info(f"No image files found in the bucket '{gcs_bucket_name}'. Please check the bucket name and its contents.")
else:
    st.info("Please create a .streamlit/secrets.toml file with your GCP configuration to begin. See the instructions for the required format.")
