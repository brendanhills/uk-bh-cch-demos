import os
from dotenv import load_dotenv

load_dotenv()

# Default models
DEFAULT_FLASH_MODEL = "gemini-3-flash-preview"
DEFAULT_PRO_MODEL = "gemini-3-pro-preview" # User requested >= 2.5

# Get from env or use default
MODEL_FLASH = os.getenv("MODEL_FLASH", DEFAULT_FLASH_MODEL)
MODEL_PRO = os.getenv("MODEL_PRO", DEFAULT_PRO_MODEL)

# Latency Configuration
# REALISTIC: Mimics real-world API delays (e.g. 30s for employment verification)
# TESTING: Near-zero latency for rapid debugging
LATENCY_MODE = os.getenv("LATENCY_MODE", "REALISTIC") 

def get_latency(min_seconds: float, max_seconds: float) -> float:
    """Returns a random latency if in REALISTIC mode, else 0."""
    import random
    if LATENCY_MODE == "TESTING":
        return 0
    return random.uniform(min_seconds, max_seconds)

# Assign roles
# Policy Expert and Underwriter might benefit from Pro's reasoning, 
# but Flash is faster for Investigator.
# For now, following user instruction to stick with 2.5 (Flash) where appropriate, 
# but user said "use pro if you need to".

# Let's use Flash for everything by default for speed/cost in demo, 
# unless specific agents need Pro. 
# User said "use pro if you need to". 
# Policy Expert (reading PDFs) and Underwriter (decision) are good candidates for Pro.
# However, 2.0 Flash is very capable. 
# Let's set defaults and allow granular override.

from google.genai import types
from google.adk.models.google_llm import Gemini

# ... existing models ...

# Helper to get model with retry logic
def get_model(model_name: str):
    """Returns a Gemini model instance with configured retry options."""
    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(
            initial_delay=1.0,
            # multiplier=2.0, # Not supported in this version
            attempts=10, # Aggressive retries for 429
            # max_delay=60.0 # Optional cap
        )
    )

INVESTIGATOR_MODEL = get_model(MODEL_FLASH)
POLICY_EXPERT_MODEL = get_model(MODEL_FLASH)
UNDERWRITER_MODEL = get_model(MODEL_FLASH)
ORCHESTRATOR_MODEL = get_model(MODEL_FLASH)
