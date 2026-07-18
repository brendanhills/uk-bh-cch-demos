import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

print(f"Listing models for {PROJECT_ID} in {LOCATION}:")
for model in client.models.list():
    print(f"- {model.name} (supports: {model.supported_actions})")
