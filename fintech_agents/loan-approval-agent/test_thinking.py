from google import genai
from google.genai import types
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def generate():
  project = os.environ.get("GOOGLE_CLOUD_PROJECT")
  location = os.environ.get("GOOGLE_CLOUD_LOCATION")

  print(f"Testing Gemini 3 Flash in {project}/{location}")

  client = genai.Client(
      vertexai=True,
      project=project,
      location=location,
      http_options={'api_version': 'v1alpha'}
  )

  msg1_image1 = types.Part.from_uri(
      file_uri="gs://cloud-samples-data/generative-ai/image/homework.png",
      mime_type="image/png",
  )

  model = "gemini-3-flash-preview"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_image1,
        types.Part.from_text(text="""Answer the question in the image with step by step solution.""")
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    seed = 0,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    thinking_config=types.ThinkingConfig(
      include_thoughts=True,
    ),
  )

  print("Sending request...")
  try:
      for chunk in client.models.generate_content_stream(
        model = model,
        contents = contents,
        config = generate_content_config,
        ):
        print(chunk.text, end="")
  except Exception as e:
      print(f"\nError: {e}")

if __name__ == "__main__":
    generate()
