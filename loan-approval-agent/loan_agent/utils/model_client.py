import logging
from google.genai import Client, types

# Cache the result to avoid repeated checks
_BEST_MODEL_NAME = None

def get_best_model_name() -> str:
    """
    Returns the name of the best available Gemini model.
    1. Tries 'gemini-3-flash-preview' (Preferred) by making a real API call.
    2. Falls back to 'gemini-2.5-flash' (Safe) if the preferred one fails (e.g. 404 or Permission Denied).
    """
    global _BEST_MODEL_NAME
    if _BEST_MODEL_NAME:
        return _BEST_MODEL_NAME

    preferred_model = "gemini-3-flash-preview"
    fallback_model = "gemini-2.5-flash"
    
    print(f"[ModelClient] Checking availability of {preferred_model}...")
    
    try:
        # Use Vertex AI as seen in gemini_3.py
        client = Client(vertexai=True)
        # Minimal generation to test access
        response = client.models.generate_content(
            model=preferred_model,
            contents="Test",
            config=types.GenerateContentConfig(max_output_tokens=1)
        )
        print(f"[ModelClient] ✅ {preferred_model} is available.")
        _BEST_MODEL_NAME = preferred_model
        
    except Exception as e:
        print(f"[ModelClient] ⚠️ {preferred_model} unavailable. Error: {e}")
        print(f"[ModelClient] 🔄 Falling back to {fallback_model} for all modules.")
        _BEST_MODEL_NAME = fallback_model

    return _BEST_MODEL_NAME
