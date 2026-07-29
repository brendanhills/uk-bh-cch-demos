from google import genai
from google.genai import types
import base64
import os

prompt="""
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
  },
  {
    "start_sec": 4.971,
    "end_sec": 6.261,
    "speaker": 1,
    "text": "Very interesting. So, how are you?",
    "timestamp": "08:25:19.2"
  },
  {
    "start_sec": 6.741,
    "end_sec": 8.441,
    "speaker": 2,
    "text": "Okay, how are you?",
    "timestamp": "08:25:21.0"
  },
  {
    "start_sec": 8.441,
    "end_sec": 11.851,
    "speaker": 1,
    "text": "I'm fine. How's everything in Philadelphia?",
    "timestamp": "08:25:22.7"
  },
  {
    "start_sec": 12.351,
    "end_sec": 13.341,
    "speaker": 2,
    "text": "Oh, pretty good.",
    "timestamp": "08:25:26.6"
  },
  {
    "start_sec": 14.071,
    "end_sec": 15.821,
    "speaker": 2,
    "text": "Just kind of busy working.",
    "timestamp": "08:25:28.3"
  },
  {
    "start_sec": 16.101,
    "end_sec": 17.391,
    "speaker": 1,
    "text": "Oh, that's good. But that's it.",
    "timestamp": "08:25:30.4"
  },
  {
    "start_sec": 17.721,
    "end_sec": 19.461,
    "speaker": 1,
    "text": "How about you?",
    "timestamp": "08:25:32.0"
  },
  {
    "start_sec": 19.461,
    "end_sec": 21.841,
    "speaker": 2,
    "text": "Oh, same thing. Just working. Yeah.",
    "timestamp": "08:25:33.7"
  },
"""

def generate():
  client = genai.Client(
      vertexai=True,
  )

  msg1_attachment = types.Part.from_uri(
      file_uri="gs://uk-bh-experiments-argolis-us/capita/4520.mp3",
      mime_type="audio/mp3",
  )


  model = "gemini-3.1-pro-preview"
  contents = [
    types.Content(
      role="user",
      parts=[
        msg1_attachment,
        types.Part.from_text(text=prompt)
      ]
    ),
  ]

  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    seed = 0,
    max_output_tokens = 65535,
    safety_settings = [types.SafetySetting(
      category="HARM_CATEGORY_HATE_SPEECH",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_DANGEROUS_CONTENT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
      threshold="OFF"
    ),types.SafetySetting(
      category="HARM_CATEGORY_HARASSMENT",
      threshold="OFF"
    )],
    thinking_config=types.ThinkingConfig(
      thinking_level="HIGH",
    ),
  )

  for chunk in client.models.generate_content_stream(
    model = model,
    contents = contents,
    config = generate_content_config,
    ):
    print(chunk.text, end="")

generate()