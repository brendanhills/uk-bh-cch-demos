import os
import google.auth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Project resolution after __init__.py cleanup
try:
    _, PROJECT_ID = google.auth.default()
except Exception:
    PROJECT_ID = None

LOCATION = None

# ALWAYS use Gemini 3 or higher.
_FLASH = os.getenv("MODEL_FLASH", "gemini-3-flash-preview").strip('"').strip("'")
_PRO = os.getenv("MODEL_PRO", "gemini-3.1-pro-preview").strip('"').strip("'")

# Fix known bad environment strings
if _FLASH == "gemini-2.5-flash":
    _FLASH = "gemini-3-flash-preview"
if _PRO == "gemini-3-pro-preview":
    _PRO = "gemini-3.1-pro-preview"

MODEL_FLASH = _FLASH
MODEL_PRO = _PRO

# Latency Configuration
# DEFAULT: TESTING (0 latency) for speed and CI reliability.
LATENCY_MODE = os.getenv("LATENCY_MODE", "TESTING") 
THINKING_LEVEL = os.getenv("THINKING_LEVEL", "MEDIUM") # Use MEDIUM for faster demo responses

def get_latency(min_seconds: float, max_seconds: float) -> float:
    """Returns a random latency if in REALISTIC mode, else 0."""
    import random
    if LATENCY_MODE == "TESTING":
        return 0
    return random.uniform(min_seconds, max_seconds)

from google.genai import types, Client
from google.adk.models.google_llm import Gemini

def get_client() -> Client:
    """Returns a configured google.genai.Client based on gemini_3.py success."""
    return Client(
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
        http_options={'api_version': 'v1beta1'}
    )

def get_model(model_name: str):
    """Returns a Gemini model instance with configured retry options."""
    # Fail fast: 1 attempt, short delay.
    return Gemini(
        model=model_name,
        retry_options=types.HttpRetryOptions(
            initial_delay=0.1,
            attempts=1, 
        ),
        http_options={'api_version': 'v1beta1'}
    )

def get_gen_config(is_pro: bool = False) -> types.GenerateContentConfig:
    """Returns a standard GenerateContentConfig with Gemini 3 settings."""
    thinking_config = None
    if is_pro:
        thinking_config = types.ThinkingConfig(thinking_level=THINKING_LEVEL)
        
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        http_options=types.HttpOptions(api_version='v1beta1'),
        thinking_config=thinking_config,
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ]
    )

INVESTIGATOR_MODEL = get_model(MODEL_FLASH)
POLICY_EXPERT_MODEL = get_model(MODEL_PRO)
UNDERWRITER_MODEL = get_model(MODEL_PRO)
ORCHESTRATOR_MODEL = get_model(MODEL_FLASH)
