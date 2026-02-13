# Real-Time Transcription Simulator

This project simulates real-time transcription of audio files stored in Google Cloud Storage (GCS) using the Google Cloud Speech-to-Text API. It is designed to demonstrate "live" transcription experiences with polished CLI output and accurate speaker attribution.

## Key Features

*   **Real-Time Simulation:** Streams audio from GCS in small chunks to simulate a live broadcast or phone call.
*   **Modular Architecture:** Separates audio source logic (GCS, streaming, mix-down) from transcription logic.
*   **Visual Polish:**
    *   **In-Column Drafts:** Displays real-time "typing" updates within the correct speaker column.
    *   **Color Coding:** Distinguishes speakers with ANSI colors (Green for Caller, Yellow for Agent).
    *   **Smart Attribution:** Detects and tags corrected speaker assignments in V1 mode.
*   **Unified Modes:** Supports toggling between high-speed "Low Latency" and high-flow "Readability" modes.

## Script Comparison

| Feature | `mono_transcribe_v1.py` | `two_channel_transcribe_v2.py` | `transcribe.py` |
| :--- | :--- | :--- | :--- |
| **API Version** | **Speech-to-Text V1** | **Speech-to-Text V2** | **Speech-to-Text V2** |
| **Audio Input** | Mixed Mono (Summed) | **Stereo (Independent)** | **Stereo (Independent)** |
| **Speaker ID** | **Diarization** (AI Voice) | **Multi-Channel** (Wire) | **Multi-Channel** (Wire) |
| **ID Reliability**| Moderate | **Perfect** | **Perfect** |
| **Speaker Labels**| Speaker 1 / 2 | **Caller / Agent** | Caller / Agent |
| **Ordering** | Stable (Single Stream) | **Dual-Mode** (Latency/Read) | Sequential (3s delay) |
| **Tuning** | Static | **Dynamic** (Gaps, Blocking) | Static (Stability Window) |
| **UI Layout** | Single Column | **Two-Column Colored** | Two-Column Colored |
| **Interim View** | Single Gray Line | **In-Column Live Drafts** | Single Gray Line |
| **Best Use Case** | Legacy 1-channel files | **Live Dashboards / Demos** | Customer Code Baseline |

## Prerequisites

1.  **Python 3.11+** and `uv` (recommended) or `pip`.
2.  **Google Cloud SDK (`gcloud`)** installed and authenticated.
    ```bash
    gcloud auth application-default login
    gcloud auth login
    ```
3.  **Environment Variables:** Copy `env.example` to `.env` and configure your project details.

---

## 1. Mono Transcription (V1)
**Script:** `mono_transcribe_v1.py`

*   **Logic:** Uses the STT **V1 API** with `enable_speaker_diarization=True`.
*   **Deduplication:** Employs fuzzy string matching to handle V1's iterative diarization updates, ensuring "corrected" sentences replace their earlier drafts rather than appearing twice.
*   **Usage:**
    ```bash
    uv run mono_transcribe_v1.py gs://your-bucket/file.mp3 --wait-for-play
    ```

## 2. Stereo Transcription (V2) - Unified
**Script:** `two_channel_transcribe_v2.py`

The primary demonstration script. Uses separate audio channels for perfect speaker identification.

*   **Usage:**
    ```bash
    # High Speed (Arrival Order)
    uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --mode low_latency

    # High Flow (Chronological Order)
    uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --mode readability
    ```

### Dual-Mode Mechanisms
The service dynamically adjusts its behavior based on the `--mode` flag using three core mechanisms implemented in `transcribe_common.py`:

1.  **Stability Threshold (`STABILITY_THRESHOLD`):**
    *   **Mechanism:** Implements a "Lookback Window." An utterance is only released to the console once the audio playhead has progressed $X$ seconds past the utterance's start time.
    *   **Purpose:** Resolves asynchronous "race conditions" between channels by allowing late-arriving past events to be sorted before display.
2.  **Gap-Based Splitting (`GAP_THRESHOLD`):**
    *   **Mechanism:** Monitors silence durations between words within a single API result. If silence exceeds the threshold, the result is partitioned into multiple chunks.
    *   **Purpose:** Breaks up long, dense monologues into smaller, natural conversational turns.
3.  **Active Interim Blocking (`ACTIVE_BLOCKING`):**
    *   **Mechanism:** Tracks the start time of "Active Interims" (ongoing speech). It blocks the release of any finalized chunk that started *after* currently active speech began.
    *   **Purpose:** Prevents short interruptions from "lapping" a long monologue that is still being processed.

| Feature | `low_latency` Mode (Default) | `readability` Mode |
| :--- | :--- | :--- |
| **Priority** | Minimum Latency (Speed) | Flow & Readability (Order) |
| **Mechanism 1: Stability** | `0.0s` (Instant print) | `1.5s` (Delayed sort) |
| **Mechanism 2: Gaps** | `Disabled` (Single block) | `0.8s` (Natural breaks) |
| **Mechanism 3: Blocking** | `Off` (Arrival order) | `On` (Strict chronological) |

---

## 3. Legacy Baseline Transcription
**Script:** `transcribe.py`

A self-contained script maintained to be as close as possible to the original code provided by the customer, while including the essential stability fixes for a readable demo.

## Testing

The project includes an integration test suite that verifies all transcription modes using a real audio source. To ensure fast execution, the tests mock playback delays and process the first 10-30 seconds of audio at maximum API speed.

### Running Tests
```bash
# Run all integration tests
uv run pytest test_transcribe_integration.py -s
```

The suite covers:
*   **V1 Mono**: Validates diarization and deduplication logic.
*   **V2 Stereo (Low Latency)**: Validates high-speed multi-channel processing.
*   **V2 Stereo (Readability)**: Validates stability buffering, active blocking, and gap-based turn splitting.
*   **Legacy Baseline**: Ensures the customer's improved baseline remains functional.

## Next Steps & Future Development

This simulator provides a robust foundation for real-time transcription. Future enhancements could include:

*   **LLM-Powered Insights:** Integration with Gemini to provide real-time summarization, intent detection, and automated "Next Action" suggestions for agents.
*   **Web-Based Dashboard:** Transitioning from a CLI to a modern React/Next.js frontend to visualize the two-column conversation with enhanced styling and sentiment heatmaps.
*   **Advanced PII Redaction:** Automatic real-time redaction of sensitive data such as credit card numbers, addresses, and account IDs using Cloud DLP.
*   **Live Translation:** Real-time translation of the conversation into multiple languages, enabling support for multi-lingual contact centers.
*   **Custom Vocabulary:** Integration of industry-specific terminology and phrases to improve accuracy for niche sectors (e.g., medical, legal, or technical support).
*   **Direct Stream Support:** Expanding beyond GCS simulation to support live streaming from WebSockets (e.g., Twilio Media Streams) or local microphone inputs.
*   **Evaluation Framework:** Developing a "Golden Set" of ground-truth transcripts. This could be achieved by running high-quality offline batch transcriptions (using Chirp 2 or 3) on the test files and then automatically comparing those results with the real-time simulated output to calculate Word Error Rate (WER) and monitor attribution drift.

---

## Architecture

*   **`simulate_audio.py`**: Handles real-time infrastructure. Throttled audio upload to match playback speed and optional mono down-mixing.
*   **`transcribe_common.py`**: The engine room. Contains the `BaseTranscriptionService` which manages the stability buffers, active-speech tracking, and the columnar UI logic.
*   **`two_channel_transcribe_v2.py`**: The unified frontend. Configures the common engine with specific thresholds for the `low_latency` and `readability` modes.

## Code Logic Walkthrough

### 1. Audio Simulation (`AudioStreamSimulator`)
The simulator mimics a live websocket stream using a static file:
1.  **Preparation:** Normalizes audio to Linear16 PCM (16-bit, 8/16kHz).
2.  **Real-Time Throttling:** Calculates the precise time each 250ms chunk *should* be sent and sleeps accordingly.

### 2. Response Processing (`process_responses`)
As API results arrive, they are routed through the following pipeline:
1.  **Interim Tracking:** The `start_time` of any draft result is recorded to inform the Blocking logic.
2.  **Turn Splitting:** Finalized results are inspected for word-level silence gaps.
3.  **Stability Buffering:** Chunks are held in a sorting queue until they are older than the `STABILITY_THRESHOLD` AND are not blocked by earlier active speech.
4.  **Columnar Rendering:** The `_print_in_column` method uses ANSI escape codes to overwrite draft lines with finalized text in real-time.