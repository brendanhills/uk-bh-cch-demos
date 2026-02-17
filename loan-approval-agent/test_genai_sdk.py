
import os
import asyncio
from google import genai
import pytest
# from dotenv import load_dotenv
# load_dotenv()

@pytest.mark.asyncio
async def test_generation():
    print("Testing generation with gemini-3-flash-preview...")
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("VERTEXAI_LOCATION", "us-central1")
    
    if not project:
        print("Error: GOOGLE_CLOUD_PROJECT not set.")
        return

    try:
        client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            http_options={'api_version': 'v1beta'}
        )
        
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents="Hello, are you Gemini 3 Flash?"
        )
        print(f"Success! Response: {response.text}")
            
    except Exception as e:
        print(f"GenAI SDK Generation Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_generation())
