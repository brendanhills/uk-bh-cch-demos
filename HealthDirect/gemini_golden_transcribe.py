import os
import json
import argparse
import mimetypes
from google import genai
from google.genai import types


# Detailed prompt from working test_gemini.py
GOLDEN_PROMPT = """
Transcribe the phone conversation between two speakers.  
Output in JSON with timestamps and speaker identification.
Be sure to accurately identify each speaker.
Accurately transcribe what they say.
It's very important that all of the conversation is correctly interlaced with 
each utterance correctly positioned in the right sequence.  

You are a producing a golden set that I can use to evaluate the quality of the 
transcription from another real-time tool. So take your time and focus on accuracy.

Here is a sample of the format I want:
[
  {
    "start_sec": 0.091,
    "end_sec": 1.371,
    "speaker": 1,
    "text": "Oh.",
    "timestamp": "08:25:14.4"
  },
  {
    "start_sec": 1.521,
    "end_sec": 3.641,
    "speaker": 1,
    "text": "Okay, Okay, this is really screwy.",
    "timestamp": "08:25:15.8"
  }
]
"""

def generate_golden_transcript(audio_path, model_id="gemini-3.1-pro-preview"):
    # Initialize the GenAI client for Vertex AI using ADC

    project = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")

    client = genai.Client(
        vertexai=True,
        project=project,
    )

    # Detect mime type
    mime_type, _ = mimetypes.guess_type(audio_path)
    if not mime_type:
        mime_type = "audio/mpeg" if audio_path.endswith(".mp3") else "audio/wav"

    print(f"Reading {audio_path} ({mime_type})...")
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    print(f"Transcribing with {model_id} via Vertex AI (Thinking: HIGH)...")

    generate_content_config = types.GenerateContentConfig(
        temperature = 1,
        top_p = 0.95,
        seed = 0,
        max_output_tokens = 65535,
        response_mime_type="application/json",
        safety_settings = [
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ],
    )
    if "3.1" in model_id:
        generate_content_config.thinking_config = types.ThinkingConfig(
            thinking_level="HIGH",
        )

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                types.Part.from_text(text=GOLDEN_PROMPT)
            ]
        ),
    ]

    response_text = ""
    audio_file_name = os.path.basename(audio_path)
    output_path = f"output/{audio_file_name}_golden_set.json"
    os.makedirs("output", exist_ok=True)
    
    print("Streaming transcription...")
    
    try:
        for chunk in client.models.generate_content_stream(
            model=model_id,
            contents=contents,
            config=generate_content_config,
        ):
            if chunk.text:
                # Progressively print to console
                print(chunk.text, end="", flush=True)
                response_text += chunk.text
        print("\nTranscription complete.")
    except Exception as e:
        print(f"\nError during generation: {e}")
        return

    try:
        # Clean up JSON if there's any markdown wrapping
        json_str = response_text.strip()
        if json_str.startswith("```json"):
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif json_str.startswith("```"):
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        transcript_data = json.loads(json_str)
        
        os.makedirs("output", exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(transcript_data, f, indent=2)
            
        print(f"Successfully generated golden transcript: {output_path} ({len(transcript_data)} entries)")
        
    except Exception as e:
        print(f"Failed to parse Gemini response: {e}")
        print("Raw Response Header:")
        print(response_text[:500])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Golden Set using Gemini 3.1")
    parser.add_argument("audio_path", help="Local path to the audio file")
    parser.add_argument("--model", default="gemini-3.1-pro-preview", help="Gemini model ID")
    
    args = parser.parse_args()
    generate_golden_transcript(args.audio_path, model_id=args.model)
