import os
import argparse
from google.cloud import storage
from google import genai
from google.genai import types 

# Construct an absolute path to the .env file.
# This makes the script independent of the current working directory,
# ensuring it works consistently in the terminal, pytest, and VS Code debugger.
from dotenv import load_dotenv
load_dotenv()


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("LOCATION")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_to_gcs(local_file_path: str, bucket_name: str, gcs_file_name: str) -> str:
    """Uploads a file to the given GCS bucket.
    Args:
        local_file_path (str): The path to the local file to upload.
        bucket_name (str): The name of the GCS bucket to upload to.
        gcs_file_name (str): The name of the file in the GCS bucket.
    Returns:
        str: The GCS URI of the uploaded file.
    """
    # The storage client will now correctly pick up the project ID from the
    # environment because load_dotenv() was called at the start of the script.
    # Explicitly passing the project is still a good practice for clarity.
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_file_name)

    blob.upload_from_filename(local_file_path)

    return f"gs://{bucket_name}/{gcs_file_name}"


def transcribe_with_gemini(audio_uri: str):
    """Transcribes an audio file from a GCS URI using the Gemini API.
    Args:
        audio_uri (str): The Google Cloud Storage URI of the input
          audio file. E.g., gs://[BUCKET]/[FILE]
    """



    audio_file = types.Part.from_uri(
        mime_type="audio/wav", # Assuming WAV. Adjust if needed.
        file_uri=audio_uri
    )

    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )
    
    prompt = types.Part.from_text(text="""
        Transcribe the following audio recording of a phone call. The recording is a customer service call. 
        Please provide a transcript that identifies each distinct speaker, including any automated systems. 
        Label each speaker as 'Speaker X' (e.g., Speaker 1, Speaker 2, etc.) and present their dialog in chronological order. 
        Provide exact timestamps for each line of dialog.
        **CRITICAL RULE: Timestamps must be in the strict HH:MM:SS format, where MM and SS are between 00 and 59.**
        The output must be formatted exactly as follows:
        00:00:00 Speaker 1: [dialog]
        00:00:05 Speaker 2: [dialog]
        ...
    """
    )

    model = "gemini-2.5-pro"

    print(f"Transcribing {audio_uri} with Gemini model {model}...")
    contents = [
    types.Content(
      role="user",
      parts=[
        audio_file,
        prompt
      ]
    )]


    generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH",threshold="OFF"), # type: ignore
                        types.SafetySetting(      category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF" ), # type: ignore
                        types.SafetySetting(      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",      threshold="OFF"    ), # type: ignore
                        types.SafetySetting(      category="HARM_CATEGORY_HARASSMENT",      threshold="OFF"    )# type: ignore
                        ], 

  )


    print("\n--- Transcription ---")
    try:
        for chunk in client.models.generate_content_stream(
            model = model,
            contents = contents[0],
            config = generate_content_config,
            ):
            if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
                continue
            print(chunk.text, end="")
                
        print("---------------------\n")
    except Exception as e:
        print(f"An error occurred during transcription: {e}")


def main():
    parser = argparse.ArgumentParser(description="Transcribe an audio file using the Gemini API.")
    parser.add_argument("audio_source", help="Path to a local audio file or a GCS URI (e.g., gs://your-bucket/audio.wav)")
    args = parser.parse_args()

    audio_source = args.audio_source

    if audio_source.startswith("gs://"):
        transcribe_with_gemini(audio_source)
    else:
        if not os.path.exists(audio_source):
            print(f"Error: Local file not found at {audio_source}")
            return
        print(f"Uploading local file {audio_source} to GCS...")
        gcs_file_name = os.path.basename(audio_source)
        gcs_uri = upload_to_gcs(audio_source, GCS_BUCKET_NAME, gcs_file_name)
        print(f"Uploaded to {gcs_uri}")
        transcribe_with_gemini(gcs_uri)


if __name__ == "__main__":
    main()
