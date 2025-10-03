
## Setup the Environment
"""

#Uncomment to update
#%pip install --upgrade google-genai

PROJECT_ID = "uk-bh-experiments-argolis" # @param {"type": "string"}
LOCATION = "us-central1" # @param {"type": "string"}
GEMINI_MODEL_NAME = "gemini-2.5-flash" # @param {"type": "string"}

"""## Calling Gemini"""

from google import genai
from google.genai import types
import base64

def generate_video_description(video_url, task_prompt, system_instruction="respond as an expert in understanding educational and training videos", stream=True):
  client = genai.Client(
      vertexai=True,
      project=PROJECT_ID,
      location=LOCATION,
  )

  #print("Setting up contents...")
  msg1_video1 = types.Part.from_uri(
      file_uri=video_url,
      mime_type="video/*",
  )

  contents = [
      types.Content(
      role="user",
      parts=[
        msg1_video1, #for processing just 1 video, place the video before the prompt https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/video-understanding#best-practices
        types.Part.from_text(text=task_prompt)
      ]
    ),
    ]

  #print("Creating gen config")
  generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 1,
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
    system_instruction=[types.Part.from_text(text=system_instruction)],
    thinking_config=types.ThinkingConfig(
      thinking_budget=-1,
    ),
  )

  #print("Generating content")
  response = []
  for chunk in client.models.generate_content_stream(
    model = GEMINI_MODEL_NAME,
    contents = contents,
    config = generate_content_config,
    ):
    response.append(chunk.text)
    if stream:
      print(chunk.text, end="")
  return "".join(response)

"""# Create Prompts for different kinds of output"""

transcript_prompt = """
          Create a transcript for this video.
          Identify the speakers for each utterance. If the names of the speakers are not known, use "speaker 1", "speaker 2" etc.
          Use the tone of voice and context to correctly link each speaker with their different utterances.
          Provide timestamps for each utterance.  The Timestamp Format is [HH:MM:SS].

          Make sure you correctly identify any voices from off camera, voice overs, or that are speaking through devices like radios or phones

          Here is an example:
            [00:00:00] Speaker 1: yeah do you want to have a have a go it's like you're doing a luge
            [00:00:07] Speaker 1: believe it or not this is real camping if you ask me believe it or not in bike packing this is a deluxe setup
            [00:00:07] Speaker 2: blimey
            [00:00:14] Speaker 2: yeah like that it's even smaller on the inside than it is on the outside
            [00:00:14] Speaker 1: that's what I'm talking about it looks a little more morbid now i'm looking at it from the outside
        """
def transcribe_video(video_url, stream=True):
  return generate_video_description(video_url, transcript_prompt, stream=stream)

description_prompt = """
Describe in words, all of the actions that happen in the video.
Your audience is a person with limited vision, so they need a concise and accurate description of the visuals of the video interspersed with the dialog.

Keep it concise, and focus on the key actions of the video that contribute to the story or lesson being taught.
The task is to communicate the intent of an educational video to a student or learner, not to provide a shot by shot analysis of the video.
Provide timestamps for each utterance.  The Timestamp Format is HH:MM:SS.

Here is an example:

Structure the output in JSON like this:
{
  "visual_description": [
    {
      "start": "00:00:00",
      "end": "00:00:03",
      "speaker": "Speaker 1",
      "text": "Recently, some friends of mine went to the Gordon Dam in Tasmania,",
      "description": "The video opens with abstract, swirling light effects, then transitions to a high-angle shot of people walking along a pathway on a massive concrete dam. The dam wall is curved and appears very tall."
    },
    {
      "start": "00:00:03",
      "end": "00:00:08",
      "speaker": "Speaker 1",
      "text": "which is 126 and a half meters or 415 feet high.",
      "description": "The camera pans upwards along the dam's curved wall, emphasizing its immense height. Numerical values for height in meters and feet overlay the screen."
    },
    {
      "start": "00:00:08",
      "end": "00:00:14",
      "speaker": "Speaker 1",
      "text": "Then, they dropped a basketball over the edge.",
      "description": "A close-up shows a person's hands wearing gloves holding a basketball over a railing. The person leans forward, and the basketball is released, falling straight down towards the base of the dam."
    },
    {
      "start": "00:00:14",
      "end": "00:00:21",
      "speaker": "Speaker 1",
      "text": "You can see that the basketball gets pushed around a bit by the breeze, but it lands basically right below where it was dropped.",
      "description": "The camera follows the basketball as it falls directly downwards, briefly swaying slightly in the air before landing on a flat, gravelly area at the dam's base. The basketball appears as a small orange dot on the ground."
    },
  ]
}

Only return the JSON object.
"""

def describe_video(video_url, stream=True):
  return generate_video_description(video_url, description_prompt, stream=stream)

"""### Prompt to extract the transcript of what the instructor is saying and writing"""

transcription_writing_prompt = """
          Create a transcript for this video of a teacher in a classroom.
          Identify the speakers for each utterance. If the names of the speakers are not known, use "speaker 1", "speaker 2" etc.
          Use the tone of voice and context to correctly link each speaker with their different utterances.
          Provide timestamps for each utterance.  The Timestamp Format is `[HH:MM:SS]`.

          Make sure you correctly identify any voices from off camera, voice overs, or that are speaking through devices like radios or phones

          If the instructor is writing something on the whiteboard or blackboard, then capture that text as well and clearly idicate it.
          Provide timestamps for writing on the board.  The Timestamp Format is `[HH:MM:SS]`.

          If there is text that is shown on screen that supports the lesson, capture that text and clearly indicate it.
          Provide timestamps for text that is shown on screen.  The Timestamp Format is `[HH:MM:SS]`.

          Here is an example:
            [00:00:00] Speaker 1: Today I would like to introduce you to the concept of height.
            [00:00:07] Speaker 1: believe it or not this is real camping if you ask me believe it or not in bike packing this is a deluxe setup
            [00:00:12] Writes on whiteboard: 'Height of the damn in meters 100m'
            [00:00:14] Speaker 1: yeah like that it's even smaller on the inside than it is on the outside
            [00:00:20] Writes on whiteboard: 'Material is concrete at 10t/m3'
            [00:00:34] Speaker 1: that's what I'm talking about it looks a little more morbid now i'm looking at it from the outside
        """

def transcribe_video_writing(video_url, stream=True):
  return generate_video_description(video_url, transcription_writing_prompt, stream=stream)

"""### Take 2 at extracting written text"""

system_instruction = """You are an expert media analysis assistant.
Your specialty is creating detailed, searchable metadata for educational video content.
Your task is to analyze a video of an instructor's lecture and generate a comprehensive, time-stamped transcript that includes both spoken dialogue and written text from the presentation."""

transcription_writing_prompt_2 = """You will be provided with the source for the video that needs to be analyzed.
  Video Source: {video_source}

  Your task is to produce a detailed transcript of the video for metadata and search purposes. Follow these instructions precisely:

  1.  Analyze the provided video source.
  2.  Create a verbatim transcript of everything the main instructor says.
  3.  For each line of dialogue, add a timestamp in the `[HH:MM:SS]` format indicating when the line was spoken.
  4.  Watch for any text the instructor writes on a whiteboard, blackboard, or digital equivalent.
  5.  Insert the written text into the transcript at the precise time it appears in the video.
  6.  Ensure your final output strictly follows the specified format below.

  **Output Format:**

  *   **Spoken Text:** Each line of spoken dialogue must start with a timestamp, followed by the speaker label \"Instructor:\".
      `[HH:MM:SS] Instructor: [Verbatim spoken text]`
  *   **Written Text:** Any text written on a board must start with a timestamp, followed by a label indicating the source (e.g., `[WHITEBOARD]:`).
      `[HH:MM:SS] [WHITEBOARD]: [Verbatim written text]`

  **Example Output:**

  [00:01:15] Instructor: Good morning, everyone. Today, we're going to discuss the principles of quantum mechanics.
  [00:01:22] Instructor: Let's start with the foundational concept.
  [00:01:25] [WHITEBOARD]: 1. Wave-Particle Duality
  [00:01:35] Instructor: As you can see here, the first principle is wave-particle duality. This means that every particle may be described as either a particle or a wave.
  [00:02:01] Instructor: Now, let's move on to our second key principle.
  [00:02:05] [WHITEBOARD]: 2. Superposition
  [00:02:15] Instructor: Superposition is the idea that a quantum system can exist in multiple states at the same time until it is measured."""

def transcribe_video_writing_2(video_url, stream=True, system_instruction=system_instruction):
  return generate_video_description(video_url, transcription_writing_prompt_2, stream=stream, system_instruction=system_instruction)

"""## Try some samples"""

## sample videos
#outside example 1 - dropping ball from dam
video_url_outside1 = "https://www.youtube.com/watch?v=2OSrvzNW9FE"

#video example 1 - football spin
video_url_outside2 = "https://www.youtube.com/watch?v=J3i3F2e4IYs"


#classroom example 1: Null Hypothesis
video_url_classroom1 = "https://www.youtube.com/watch?v=_Qlxt0HmuOo"

#classroom example 2: Finding the greatest common factor
video_url_classroom2 = "https://www.youtube.com/watch?v=_HRUfi4PRk4"

#classroom example 3: Multiply Whole Numbers By Fractions
video_url_classroom3 = "https://www.youtube.com/watch?v=Z757THlXLA8"

"""## Transcribing Only"""

### transcribing an outside lesson - dropping ball from dam

transcribe_video(video_url_outside1)

#describing a video lesson - ball spin

transcribe_video(video_url_outside2)

"""## Describing the scene as well as transcribing"""

### describe and transcribe an outside lesson - dropping ball from dam

describe_video(video_url_outside1)

#describing and transcribe a video lesson - ball spin

describe_video(video_url_outside2)

"""## Transcribe and Extract Text"""

# extracting speech and writing - v1, example 1: Null Hypothesis

transcribe_video_writing(video_url_classroom1)

## extracting speech and writing - v1, example 2: Finding the greatest common factor

transcribe_video_writing(video_url_classroom2)

## extracting speech and writing - v1, example 3: Multiply Whole Numbers By Fractions

transcribe_video_writing(video_url_classroom3)

"""### Version 2 of Speaking and Writing"""

## extracting speech and writing - v2, example 1: Multiply Whole Numbers By Fractions

transcribe_video_writing_2(video_url_classroom1)

## extracting speech and writing - v2, example 2: Multiply Whole Numbers By Fractions

transcribe_video_writing_2(video_url_classroom2)

## extracting speech and writing - v2, example 3: Multiply Whole Numbers By Fractions

transcribe_video_writing_2(video_url_classroom3)