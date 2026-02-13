from vertexai.generative_models import GenerativeModel, GenerationConfig, GenerationResponse
import vertexai

GOOGLE_CLOUD_PROJECT = "uk-bh-experiments-argolis"
GOOGLE_CLOUD_LOCATION = "us-central1"
GEMINI_MODEL_NAME = "gemini-2.5-flash"

vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

model = GenerativeModel(
  GEMINI_MODEL_NAME,
  system_instruction=[
    "Talk like a pirate.",
    "Don't use rude words.",
  ],
)

response = model.generate_content(
  "Why is sky blue?",
  generation_config=GenerationConfig(temperature=0),
)

print(response)