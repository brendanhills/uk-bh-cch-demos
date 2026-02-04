# Real-Time Transcription Simulator

This project simulates real-time transcription of audio files stored in Google Cloud Storage (GCS) using the Google Cloud Speech-to-Text API. It is designed to demonstrate "live" transcription experiences with polished CLI output and accurate speaker attribution.

## Key Features

*   **Real-Time Simulation:** Streams audio from GCS in small chunks to simulate a live broadcast or phone call.
*   **Modular Architecture:** Separates audio source logic (GCS, streaming, mix-down) from transcription logic.
*   **Visual Polish:**
    *   **Interim Results:** Displays real-time "Draft" updates as words are spoken.
    *   **Color Coding:** Distinguishes speakers with ANSI colors (Green for Caller, Orange for Agent).
    *   **Smart Attribution:** Detects and tags corrected speaker assignments with a bold red `[RE-ATTRIBUTED]` label.
*   **Playback Sync:** Generates a clickable **Google Cloud Console URL** (with your active `gcloud` account) so you can listen to the audio while watching the transcription.
*   **Demonstrate/Tests Two Different Transcription Modes:**
    *  Both approaches assume that the audio is has 2 channels - one with each speaker on a phone call.
    *   **Mono (V1):** Uses STT V1 API with Diarization.  Merges two channels into a single-channel audio in real time.
    *   **Two Channel (V2):** Uses STT V2 API with Multi-Channel recognition.

## Prerequisites

1.  **Python 3.11+** and `uv` (recommended) or `pip`.
2.  **Google Cloud SDK (`gcloud`)** installed and authenticated.
    ```bash
    gcloud auth application-default login
    gcloud auth login  # Required for generating the Console URL with ?authuser
    ```
3.  **Environment Variables:** Copy `env.example` to `.env` and configure your project details.

## 1. Mono Transcription (V1)
**Script:** `mono_transcribe_v1.py`

Demonstrates using the Speedch diarization option where two speakers are on a single channel.

*   **Logic:** Uses the Google Cloud Speech-to-Text **V1 API** with `enable_speaker_diarization=True`.
*   **Diarization:** AI analyzes voice signatures to distinguish speakers.
*   **On-the-Fly Mix-down:** The `simulate_audio.py` script automatically merges stereo channels into a single mono stream chunk-by-chunk to simulate processing a multi channel source.
*   **Output:** Single column with `[Speaker 1]` or `[Speaker 2]` labels.

### Usage
```bash
uv run mono_transcribe_v1.py gs://your-bucket/file.mp3 --wait-for-play
```

## 2. Stereo Transcription (V2)
**Script:** `two_channel_transcribe_v2.py`

Demonstratesusing multi channel processing where Agent and Caller are on separate channels.

*   **Logic:** Uses the Google Cloud Speech-to-Text **V2 API** with `multi_channel_mode=SEPARATE_RECOGNITION_PER_CHANNEL`.
*   **Speaker ID:** Maps audio channels directly to "Caller" vs "Agent" (highly reliable).
*   **Output:** **Two-column layout** (Left for Caller, Right for Agent) for easy reading of conversational flow.  Has additional logic to keep the output in the right order.

### Usage
```bash
uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --wait-for-play
```

## Common Arguments

*   `gcs_uri`: The full `gs://...` path to your audio file.
*   `--wait-for-play`: Pauses execution after generating the Console URL, allowing you to start audio playback before transcription begins so you can listen to the audio as it's being transcribed.
*   `--customer-channel`: (Stereo only) Specify which channel is the customer (`channel_1` or `channel_2`).  

---

## Architecture

*   **`simulate_audio.py`**: A standalone module that handles the "Real-Time Simulation" infrastructure:
    *   GCS File Download & Google Console URL generation.
    *   Audio property inspection (using `pydub`).
    *   **Throttled Streaming:** An async generator that "plays" the file chunks.
    *   **On-the-Fly Conversion:** Mixes down stereo chunks to mono in real-time if required.
*   **`transcribe_common.py`**: Contains the base transcription logic (UI helpers, deduplication, and V2 API scaffolding).
*   The scripts (`mono_transcribe_v1.py` and `two_channel_transcribe_v2.py`) instantiate the simulator and pipe the resulting stream into the transcription service.

## Code Logic Walkthrough

### 1. Audio Simulation (`AudioStreamSimulator`)
The simulator mimics a live websocket or microphone stream using a static file:
1.  **Preparation:** It downloads the file and standardises it to raw Linear16 PCM data.
2.  **The Stream Generator:** It slices the file into small chunks (default is 250ms) of audio.
3.  **Real-Time Throttling:** It calculates the playback duration of each chunk and **sleeps** accordingly. This ensures the transcription happens at the actual speed of conversation.
4.  **On-the-Fly Mono:** For the Mono approach, it uses `audioop` to mix stereo channels down to one *per chunk* as they are yielded.

### 2. API Request Generation (`generate_requests`)
The transcription service consumes the iterator from the simulator:
*   **First Request:** Contains the *Configuration* (Codec, Sample Rate, Model, Diarization settings).
*   **Subsequent Requests:** As the simulator yields audio chunks, the generator wraps them in API requests and sends them to Google.

### 3. Deduplication & Re-attribution
The V1 Diarization API can be "jittery," sometimes re-sending a slightly corrected version of a sentence.
*   **Logic:** We maintain a `speaker_history` buffer. We use `difflib` (sequence matching) to see if a incoming chunk is a duplicate or a re-attribution (same text, different speaker).
*   **Tagging:** If the system changes its mind about who said something, it marks the line with a bold red **`[RE-ATTRIBUTED]`** tag.

### 4. UI Polish & Interim Results
The real-time typing effect is achieved by handling **Interim Results** (`is_final=False`):
*    tentative transcripts are printed immediately with a `... ` prefix.
*   In Stereo (V2), we currently print these on new lines to provide a stable, readable "scrolling thought" log.
*   When a result becomes **Final**, the interim line is cleared (using `\r\033[K`), and the permanent, color-coded text is printed.
*   In Stereo (V2) mode we detect any chunks that are out of order and flag those `Out of order: 🚨`

### 5. Playback Synchronization (`--wait-for-play`)
1.  The script generates a link to the Google Cloud Console for the file.
2.  It appends `?authuser=...` using your active local `gcloud` account.
3.  It pauses with `input()`. Upon Enter, it resets the internal `start_time` to `now()`, ensuring the transcription timestamps match your playback.
