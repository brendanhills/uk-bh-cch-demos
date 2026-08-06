# Specification: Merge Live Translate Demo into Web Server (`merge_live_translate_20260715`)

## Overview
Currently, `live_translate_demo.py` (located in the root directory) and `demo/web_server.py` are separate scripts with redundant code for loading stereo files, splitting channels, managing Gemini Live sessions, and printing console rows.
This track aims to merge `live_translate_demo.py` directly into `demo/web_server.py`. The unified file `demo/web_server.py` will support two modes of operation:
1. **Server Mode (Default)**: Launches the FastAPI web server to serve the frontend interface and handle real-time WebSockets.
2. **CLI Mode (via `--cli` flag)**: Runs as a standalone command-line application that streams audio and translates bidirectionally, completely matching and extending the current functionality of `live_translate_demo.py`.

Both modes will be driven by a unified, central configuration file (`demo/interpreter_config.json`) containing all settings.

## Functional Requirements

### 1. Unified Configuration File (`demo/interpreter_config.json`)
- Create/expand a single JSON-based configuration file to manage all settings for both CLI and Server modes:
  ```json
  {
    "model_name": "gemini-3.5-live-translate-preview",
    "chunk_ms": 40,
    "pacing_mode": "paced", // "simple" or "paced"
    "enable_playback": false,
    "enable_stats": false,
    "enable_glossary": true,
    "pacing": {
      "turn_timeout_sec": 15.0,
      "ceased_audio_threshold": 4.5,
      "startup_audio_threshold": 15.0,
      "additional_pause_sec": 2.0
    },
    "presets": {
      "german": {
        "file": "samples/de_fever_session.wav",
        "code": "de",
        "language": "German"
      }
    }
  }
  ```
- The application (CLI or Server) will load this file on startup, using its values as defaults.

### 2. Unified Command-Line Interface (`demo/web_server.py`)
- Add command-line argument parsing to `demo/web_server.py`.
- If the `--cli` flag is provided, `demo/web_server.py` will bypass the FastAPI app startup (uvicorn) and execute the CLI translation demo directly in the console.
- Supported CLI Arguments (overriding config file defaults):
  - `--cli`: Enable CLI mode.
  - `--config`: Path to a custom JSON configuration file (defaults to `demo/interpreter_config.json`).
  - `--preset`: Select a preset medical call (e.g., `german`, `spanish`, `vietnamese`, `arabic`).
  - `--file`: Path to a custom stereo WAV file input.
  - `--language-code`: Override target language code (e.g., `de`, `es`, `vi`, `ar`).
  - `--language`: Override target language name (e.g., `German`, `Spanish`, `Vietnamese`, `Arabic`).
  - `--model`: Override the Gemini Live model.
  - `--pacing`: Choose between `simple` direct streaming and `paced` streaming.
  - `--playback`: Flag to enable real-time local audio playback of translated streams through local speakers.
  - `--no-glossary`: CLI switch to disable glossary priming.
  - `--stats`: Flag to log detailed frame-by-frame audio streaming stats and latency metrics to the console.
  - `--chunk-ms`: Configurable streaming chunk size in milliseconds (e.g., `20`, `40`, `100`).

### 3. Pacing Engine Integration
- Extract or adapt the advanced pacing/cooldown state machine used in `web_server.py` so that it is a reusable generator/loop logic.
- Ensure the CLI mode can either:
  - Stream chunks at direct intervals (simple direct-stream).
  - Utilize the full turn-taking, silence-streaming, and cooldown mechanisms (paced mode).

### 4. Output Audio & Analysis
- Automatically save translated outputs as raw PCM/WAV files in the `output/` directory.
- Optional: Playback translations in real-time through the default system audio device if optional dependencies are met.
- Support a developer evaluation mode (`--stats`) that logs latency, cumulative sent/received bytes, frame counts, and chunk processing times.

### 5. Code Consolidation & Parity
- Ensure there is zero functionality loss for both the browser-side web application and the terminal-side CLI tool.
- Remove the redundant root-level `live_translate_demo.py` script once verified, or replace it with a simple wrapper calling `demo/web_server.py --cli`.

### 6. Gemini Live API Best Practices Alignment
- **Configurable 20ms - 100ms Chunk Streaming**: Support transmitting audio in precise chunks, defaulting to **40ms** (`--chunk-ms 40`) to ensure minimal latency and optimal Live API performance.
- **Structured System Instructions**: Follow the structured SI layout (Persona, Conversational Rules, and Guardrails) for sessions. Ensure non-English prompt target segments explicitly append: `RESPOND IN {OUTPUT_LANGUAGE}. YOU MUST RESPOND UNMISTAKABLY IN {OUTPUT_LANGUAGE}.`
- **Interruption Handling**: In both CLI and Web Server modes, handle `"interrupted": true` signals in the WebSocket `server_content` response by immediately discarding local audio/playback buffers and stopping active playback.
- **Low Latency & Resampling**: Ensure input audio is correctly down-sampled to 16kHz.
- **Session Resilience & Signals**: Gracefully listen to and handle `GoAway` messages (using `timeLeft`) and `generationComplete` signals in session loops.

## Acceptance Criteria
1. Running `uv run demo/web_server.py` without `--cli` starts the FastAPI server as normal, driven by configuration defaults in `demo/interpreter_config.json`.
2. Running `uv run demo/web_server.py --cli --preset german` starts the CLI-based bidirectional real-time translator in the terminal with colored speaker side-by-side columns.
3. The CLI supports all custom arguments, including `--file`, `--model`, `--pacing`, `--playback`, `--stats`, and `--chunk-ms`, overriding settings in the config file.
4. Automated tests are implemented to verify command-line argument parsing, config file loading, and CLI mode execution.

## Out of Scope
- Rewriting frontend HTML/JS files in `demo/web/`.
- Changing default glossary entries in `dictionary/glossary.json`.
