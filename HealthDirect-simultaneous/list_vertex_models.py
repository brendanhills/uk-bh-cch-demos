import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=GCP_PROJECT_ID,
    location=GCP_LOCATION
)

print(f"Listing models in {GCP_LOCATION}...")
for model in client.models.list():
    print(f" - {model.name}")
