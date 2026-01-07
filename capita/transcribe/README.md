# Transcription Service

This service transcribes audio files stored in Google Cloud Storage (GCS) using the Google Cloud Speech-to-Text API. It supports both unbuffered and buffered transcription, as well as handling multi-channel audio with speaker identification.

## Setup

### Prerequisites

*   Python 3.9+
*   [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured with appropriate permissions to access Speech-to-Text API and GCS.
*   A Google Cloud Project with the Speech-to-Text API enabled.

### Environment Variables

Create a `.env` file in the root directory of the project based on the `env.example` file. This file will contain your Google Cloud project configuration.

```bash
cp env.example .env
# Open .env and fill in the values
```

Here's an explanation of the variables in `.env`:

*   `PROJECT_ID`: Your Google Cloud Project ID.
*   `LOCATION`: The Google Cloud region where your Speech-to-Text recognizer will be created (e.g., `us-central1`).
*   `GOOGLE_CLOUD_PROJECT`: Should typically be the same as `PROJECT_ID`.
*   `GCS_BUCKET_NAME`: The name of the GCS bucket where your audio files are stored.
*   `GCP_RECOGNIZER_ID`: A unique ID for the Speech-to-Text recognizer to be used or created.
*   `GCP_TRANSCRIPTION_MODEL`: The Speech-to-Text model to use (e.g., `telephony`, `latest_long`).
*   `LANGUAGE_CODE` (Optional): The language code for transcription (default: `en-US`).
*   `CUSTOMER_CHANNEL` (Optional): Specifies which audio channel represents the customer (`channel_1` or `channel_2`). Default is `channel_1`.

## Usage

Run the `transcribe.py` script with the GCS URI of your audio file.

### Basic Command

```bash
python transcribe.py gs://your-bucket-name/path/to/your/audio.wav
```

### Options

*   **`gcs_uri`** (Required): The full Google Cloud Storage URI of the audio file you want to transcribe (e.g., `gs://my-audio-bucket/call_recording.wav`). The script currently processes WAV files.
*   **`--customer-channel`** (Optional): Specifies which channel contains the customer's audio.
    *   `channel_1`: (Default) Assumes channel 1 is the customer.
    *   `channel_2`: Assumes channel 2 is the customer.
    *   Example: `python transcribe.py gs://my-audio-bucket/call.wav --customer-channel channel_2`
*   **`--use-buffered`** (Optional, flag): Enables buffered transcription. This processes results in chunks, potentially improving latency for long audio files or when real-time processing of partial results is desired.
    *   Example: `python transcribe.py gs://my-audio-bucket/call.wav --use-buffered`
*   **`--buffer-timeout`** (Optional): When `--use-buffered` is enabled, this sets the timeout in seconds for flushing buffered results. Default is `0.5` seconds.
    *   Example: `python transcribe.py gs://my-audio-bucket/call.wav --use-buffered --buffer-timeout 1.0`

### Example Commands

Transcribe a mono audio file:
```bash
python transcribe.py gs://your-bucket/mono_audio.wav
```

Transcribe a stereo audio file, identifying customer on channel 2:
```bash
python transcribe.py gs://your-bucket/stereo_call.wav --customer-channel channel_2
```

Transcribe with buffering enabled and a 1-second buffer timeout:
```bash
python transcribe.py gs://your-bucket/long_conversation.wav --use-buffered --buffer-timeout 1.0
```

## Output

The script will generate a JSON file named `output.json` in the current directory. This file will contain a list of transcribed segments, each including:

*   `speaker`: Identifies the speaker as "customer" or "agent".
*   `text`: The transcribed text for that segment.
*   `timestamp`: The end timestamp of the transcribed segment.

Example `output.json`:

```json
[
  {
    "speaker": "customer",
    "text": "Hello, how can I help you today?",
    "timestamp": "2023-10-27 10:00:05"
  },
  {
    "speaker": "agent",
    "text": "I'm looking for information about my account.",
    "timestamp": "2023-10-27 10:00:10"
  }
]
```
