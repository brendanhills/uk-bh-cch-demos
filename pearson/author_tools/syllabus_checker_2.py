import streamlit as st
from google.cloud import storage
import google.genai as genai

# Initialize Google Cloud Storage client
storage_client = storage.Client()

# Function to upload file to GCS
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to Google Cloud Storage."""
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# Function to validate chapter content against learning objectives
def validate_chapter(learning_objectives, chapter_content):
    """Validates chapter content against learning objectives using Gemini."""
    # Placeholder for Gemini integration
    # In a real implementation, this function would use the Gemini API
    # to analyze the chapter content and provide feedback.

    model = genai.GenerativeModel('gemini-2.0-pro')
    prompt = f"""
    You are a helpful assistant that can check if a textbook chapter meets the stated learning objectives.
    I will provide you with the chapter content and the list of learning objectives.
    You need to check if the chapter covers all the objectives listed.
    If the textbook covers all the topics, you should say "Yes".
    If the textbook does not cover all the topics, you should say "No" and list the topics that are missing.
    Here is the  content:
    {chapter_content}
    Here are the learning objectives:
    {learning_objectives}
    Does the textbook meet the objectivess?
    """
    response = model.generate_content(prompt)
    # Display the response
    st.success(response.text)

    met_objectives = []
    recommended_updates = []
    for objective in learning_objectives:
        if objective.lower() in chapter_content.lower():
            met_objectives.append(objective)
        else:
            recommended_updates.append(f"Objective '{objective}' not clearly addressed.")
    return met_objectives, recommended_updates

# Streamlit app
def main():
    st.title("Textbook Content Validation App")

    # Sidebar for settings
    st.sidebar.header("Settings")
    bucket_name = st.sidebar.text_input("GCS Bucket Name", "your-gcs-bucket-name")

    # Input for learning objectives
    st.header("Learning Objectives")
    learning_objectives = st.text_area("Enter learning objectives (one per line)",
                                      "Understand the basics of Python.\nLearn about data structures.\nMaster object-oriented programming.")
    learning_objectives = learning_objectives.splitlines()

    # File uploader for chapter draft
    st.header("Chapter Draft")
    uploaded_file = st.file_uploader("Upload chapter draft", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        # Save uploaded file to GCS
        file_path = "temp_chapter." + uploaded_file.name.split(".")[-1]
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        blob_name = f"chapters/{uploaded_file.name}"
        upload_blob(bucket_name, file_path, blob_name)
        st.success(f"File uploaded to GCS: {blob_name}")

        # Check chapter content against learning objectives
        if st.button("Check Chapter"):
            with st.spinner("Validating chapter content..."):
                # Read file from GCS
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                chapter_content = blob.download_as_text()

                met_objectives, recommended_updates = validate_chapter(learning_objectives, chapter_content)

                # Display results
                st.header("Validation Results")
                st.subheader("Objectives Met")
                if met_objectives:
                    for objective in met_objectives:
                        st.success(objective)
                else:
                    st.info("No objectives met.")

                st.subheader("Recommended Updates")
                if recommended_updates:
                    for update in recommended_updates:
                        st.warning(update)
                else:
                    st.success("No updates recommended.")

if __name__ == "__main__":
    main()
