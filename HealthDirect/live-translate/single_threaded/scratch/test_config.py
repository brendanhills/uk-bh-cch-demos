import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set")
        return
    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                silence_duration_ms=400
            )
        )
    )
    print("Config created successfully!")
    print(config)

if __name__ == "__main__":
    test()
