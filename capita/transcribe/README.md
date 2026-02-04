# Real-Time Transcription Simulator

This project simulates real-time transcription of audio files stored in Google Cloud Storage (GCS) using the Google Cloud Speech-to-Text API. It is designed to demonstrate "live" transcription experiences with polished CLI output.

## Key Features

*   **Real-Time Simulation:** Streams audio from GCS in chunks to simulate a live broadcast or phone call.
*   **Visual Polish:**
    *   **Interim Results:** Displays real-time "..." updates as words are spoken.
    *   **Color Coding:** Distinguishes speakers with ANSI colors (Green for Speaker 1/Caller, Orange for Speaker 2/Agent).
    *   **Clean Output:** Uses smart cursor manipulation to prevent "flicker" or ghosting during updates.
*   **Playback Sync:** Generates a clickable **Google Cloud Console URL** (with your active `gcloud` account) so you can listen to the audio while watching the transcription.
*   **Two Specialized Modes:**
    *   **Mono (V1):** Uses STT V1 API with Diarization for mixed single-channel audio.
    *   **Stereo (V2):** Uses STT V2 API with Multi-Channel recognition for split-channel telephony.

## Prerequisites

1.  **Python 3.9+** and `uv` (recommended) or `pip`.
2.  **Google Cloud SDK (`gcloud`)** installed and authenticated.
    ```bash
    gcloud auth application-default login
    gcloud auth login  # Required for generating the Console URL with ?authuser
    ```
3.  **Environment Variables:** Copy `env.example` to `.env` and configure your project details.

## 1. Mono Transcription (V1)
**Script:** `mono_transcribe_v1.py`

Best for **mixed audio** where multiple speakers are on a single track (or you want to force mono processing).

*   **Logic:** Uses the Google Cloud Speech-to-Text **V1 API** with `enable_speaker_diarization=True`.
*   **Diarization:** Distinguishes speakers based on voice signatures.
*   **Output:** Single column, but prefixed with `[Speaker 1]` or `[Speaker 2]`.

### Usage
```bash
uv run mono_transcribe_v1.py gs://your-bucket/file.mp3 --wait-for-play
```

## 2. Stereo Transcription (V2)
**Script:** `two_channel_transcribe_v2.py`

Best for **telephony audio** where the Agent and Caller are recorded on separate tracks (Channel 1 vs Channel 2).

*   **Logic:** Uses the Google Cloud Speech-to-Text **V2 API** with `multi_channel_mode=SEPARATE_RECOGNITION_PER_CHANNEL`.
*   **Speaker ID:** Maps Channel 1 to "Caller" (Green) and Channel 2 to "Agent" (Orange) by default (configurable).
*   **Output:** **Two-column layout** (Left for Channel 1, Right for Channel 2) for easy reading of conversation flow.

### Usage
```bash
uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --wait-for-play
```

## Common Arguments

*   `gcs_uri`: The full `gs://...` path to your audio file.
*   `--wait-for-play`: Pauses execution after generating the Console URL, allowing you to start audio playback before transcription begins.
*   `--use-buffered`: Enables buffering to smooth out results (reduces "jumping" but adds slight latency).
*   `--customer-channel`: (Stereo only) Specify which channel is the customer (`channel_1` or `channel_2`).

## Architecture

*   **`transcribe_common.py`**: Contains the `BaseTranscriptionService` which handles:
    *   GCS File Download & Signed URL generation.
    *   Audio format conversion (using `pydub`).
    *   Streaming simulation queue.
    *   ANSI UI helper methods.
*   The scripts inherit from this base to implement their specific V1 or V2 API logic.

## Deep Dive: Mono vs. Stereo Attribution

A key part of this demo is showing how we identify "Who is speaking." The two scripts use fundamentally different methods:

### 1. Mono Logic (Speaker Diarization)
Used in `mono_transcribe_v1.py`.
*   **The Problem:** Both voices are mixed on one audio track.
*   **The Solution:** We use **Diarization**. The AI analyzes the "voiceprint" (pitch, tone, cadence) of the audio.
*   **How it works in code:** 
    1. When a sentence is finalized, the API returns a list of words. 
    2. Each word is tagged with a speaker number (e.g., `word.speaker_tag = 1`). 
    3. Our script groups these words by their tags and assigns the corresponding color.
    4. This is "Intelligence-based" separation.

### 2. Stereo Logic (Multi-Channel)
Used in `two_channel_transcribe_v2.py`.
*   **The Problem:** We have two distinct tracks (Left/Right), and we need to map them to "Caller" vs "Agent" without guessing.
*   **The Solution:** We use **Channel Mapping** with the V2 API. 
*   **How it works in code:** 
    1. **V2 Telephony Model:** We use Google's V2 API, specifically the `telephony` model, which is optimized for 8kHz call center audio.
    2. **Separate Recognition:** We tell the API `multi_channel_mode=SEPARATE_RECOGNITION_PER_CHANNEL`. This transcribes both tracks independently and simultaneously.
    3. **Role Mapping:** The script takes your `--customer-channel` argument (e.g., "Channel 1") and maps it to the **"Caller"** role. The other channel automatically becomes the **"Agent"**.
    4. **Split-Column View:** Unlike Mono's single list, Stereo uses a **two-column layout**. Caller text is aligned Left, and Agent text is indented 60 spaces to the Right. This makes it easy to visually scan interruptions and conversational "ping-pong."
    5. **Out-of-Order Handling:** Because the two channels are processed in parallel, a short word from the Agent might arrive *before* a long sentence from the Caller. The script tracks timestamps and displays a `Warn: 🚨` if lines appear out of sequence. Enabling `--use-buffered` resolves this by sorting results before display.

## Code Logic Walkthrough

This section explains how the code works, useful for understanding the implementation details during a demo.

### 1. Audio Preparation (`prepare_audio`)
Before any transcription happens, the script:
1.  **Downloads** the file from GCS into memory.
2.  **Inspects** it using `pydub` (ffmpeg wrapper) to determine sample rate and channel count.
3.  **Standardises** the audio to raw Linear16 PCM data. This ensures the Google Speech API receives exactly the format it expects, preventing encoding errors.

### 2. Streaming Simulation (`stream_audio_chunks`)
To simulate a live broadcast or phone call using a static file:
1.  The audio byte array is split into small chunks (e.g., 8000 bytes).
2.  The script calculates how much "time" each chunk represents (e.g., 250ms).
3.  It pushes a chunk to an `asyncio.Queue` and then **sleeps** for that duration.
4.  This forces the transcription loop to process data at the speed of human speech, creating the "live" effect.

### 3. API Request Generation (`generate_requests`)
The code uses a Python generator to yield requests to the Google API:
*   **First Request:** Contains the *Configuration* (Codec, Sample Rate, Model, Diarization settings).
*   **Subsequent Requests:** Contain only the *Audio Bytes* popped from the streaming queue.

### 4. UI Polish & Interim Results
The "magical" real-time typing effect is achieved by handling **Interim Results** (`is_final=False`):
*   **V1 (Mono):** The API sends tentative transcripts ("..."). We print these to the console with `\r` (carriage return) and `\033[2K` (clear line) codes. This allows the text to "update" in place without flooding the terminal.
*   **V2 (Stereo):** Similar logic, but we also track the `channel_tag` to potentially display activity indicators (`1`, `2`) if text isn't available yet.

When a result becomes **Final** (`is_final=True`), we:
1.  Clear the last interim line.
2.  Format the final text with **ANSI Colors** (Green/Orange).
3.  Print it permanently to the log.
4.  Reset the interim tracking state.

### 5. Playback Synchronization (`--wait-for-play`)
To allow you to demo the audio and text in sync:
1.  The script generates a link to the Google Cloud Console for the specific file.
2.  It appends `?authuser=...` using your local gcloud credential to ensure the link works immediately.
3.  It pauses execution with `input()` until you press Enter.
4.  Upon Enter, it resets its internal `start_time` timestamp to `now()`, ensuring the printed logs match the wall-clock time of your playback.
