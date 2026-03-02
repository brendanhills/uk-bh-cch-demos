from google import genai
from google.genai import types
import os
import google.auth

def generate():
  # VS Code automatically injects .env vars. If the project in .env is incorrect,
  # it breaks the client. Unset them to force usage of the working gcloud ADC defaults.
  os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
  os.environ.pop("GOOGLE_CLOUD_LOCATION", None)

  _, project = google.auth.default()
  print(f"Using Project: {project}")
  print("Using Location: us-central1 (default)")

  client = genai.Client(
      vertexai=True,
      project=project,
      http_options={'api_version': 'v1beta1'},
  )

  models = ["gemini-3.1-pro-preview", "gemini-3-pro-preview", "gemini-3-flash-preview"]

  print("Setting up contents...")
  contents = [
    types.Content(
      role="user",
      parts=[
        types.Part.from_text(text="""write a haiku""")
      ]
    ),
  ]

  print("Creating gen config")

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
  )

  for model in models:
    print(f"\n--- Testing Model: {model} ---")
    try:
      print("Generating content...")
      for chunk in client.models.generate_content_stream(
        model = model,
        contents = contents,
        config = generate_content_config,
        ):
        print(chunk.text or "", end="")
      print()
    except Exception as e:
      print(f"\nError with {model}: {e}")

generate()