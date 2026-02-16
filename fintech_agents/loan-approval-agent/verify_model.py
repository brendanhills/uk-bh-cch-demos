
from google.adk import Agent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
import asyncio
import sys
import os
import os
from dotenv import load_dotenv

load_dotenv()

from loan_approval_agent.config import MODEL_FLASH

MODEL_TO_TEST = MODEL_FLASH

async def test_model():
    print(f"Testing model: {MODEL_TO_TEST}...")
    
    project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION") or os.environ.get("VERTEXAI_LOCATION") or "us-central1"
    
    if not project:
        print("\n[ERROR] GOOGLE_CLOUD_PROJECT environment variable is not set.")
        print("Please run: export GOOGLE_CLOUD_PROJECT=<your-project-id>")
        return False
        
    print(f"Project: {project}")
    print(f"Location: {location}")

    # Check for PDF policies
    policy_dir = "loan_approval_agent/data/policy_docs"
    pdfs = [f for f in os.listdir(policy_dir) if f.endswith(".pdf")] if os.path.exists(policy_dir) else []
    if len(pdfs) < 3:
        print(f"\n[WARNING] Only found {len(pdfs)} policy PDFs in {policy_dir}. Expected 3.")
        print("Please run: uv run generate_policy_pdfs.py")
    else:
        print(f"Found {len(pdfs)} policy PDFs.")

    try:
        agent = Agent(model=MODEL_TO_TEST, name="test_agent")
        runner = InMemoryRunner(agent=agent)
        session = await runner.session_service.create_session(
             app_name=runner.app_name, user_id="test_user"
        )
        
        # Simple hello to trigger the model
        content = UserContent(parts=[Part(text="Hello, are you there?")])
        
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                print(f"Success! Response: {event.content.parts[0].text[:50]}...")
                return True
                
    except Exception as e:
        print(f"Model {MODEL_TO_TEST} failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_model())
    if not success:
        sys.exit(1)
