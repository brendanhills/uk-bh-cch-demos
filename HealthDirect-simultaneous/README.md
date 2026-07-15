# Real-Time Bilingual Medical Interpreter (HealthDirect Experiment)

This project is a high-fidelity, real-time bidirectional bilingual interpreter designed for clinical interactions (such as a call between a non-English-speaking patient and a HealthDirect nurse). It utilizes the **Gemini Live API** to translate multi-channel audio stream inputs in real-time, matching clinical terms against a customized, scraped dictionary and rendering highlights dynamically in both a dual-column terminal CLI and an interactive web interface.

---

## Key Features

- **Dual-Model Support & Evaluation**: Supports both **Gemini 3.5 Live Translate (Preview)** and **Gemini 3.1 Flash Live + Glossary** modes, with a dynamic Model Selector in the Web UI. Specifically resolves the WebSocket 1011 internal error under Gemini 3.5 by bypassing redundant silence/heartbeat streaming during generation.
- **Dynamic Voice Gender Selection**: Automatically assigns appropriate male/female TTS voices (e.g., Puck/Charon vs. Kore/Aoede) matching the speaker's specified gender in `LiveConnectConfig`.
- **Low-Latency Real-Time Text Streaming**: Intercepts real-time text parts (`parts[].text`) from the Gemini Live stream and immediately forwards low-latency transcripts to the client WebSocket interface.
- **Resilient Audio Power Envelope Pacing**: Resolves pacing hangs and freezes under standard models. Features an intelligent activity monitor that automatically proceeds with the next turn if translated audio ceases for $> 1.5$ seconds or fails to play back within a $4.0$-second startup window. For native translation models (Gemini 3.5), the state machine intelligently avoids streaming inactive/active silence to ensure session stability.
- **Strict Clinical Glossary Enforcement**: When utilizing Gemini 3.1, frontloads a customized passive interpreter system prompt with Australian terminology spellings and a formatted glossary list to enforce absolute vocabulary dominance in translated audio text.
- **Real-Time Bidirectional Translation**: Establishes dual parallel **Gemini Live API WebSocket** streams to translate patient speech (e.g., German, Spanish, Vietnamese, Arabic) to English and clinician speech (English) to the patient's language concurrently.
- **Stereo Channel Splitting**: Loads stereo `.wav` audio files and separates them into independent mono feeds—the Left channel represents the Patient (foreign language) and the Right channel represents the Nurse (English).
- **Multi-Destination Turn-Aggregated Logging**:
  - Automatically initializes and writes conversational transcripts block-by-turn to both standard output and `conversation_transcript.log`.
  - Captures full text representation for each turn: speaker name, original transcript, and translated content.
- **Clinical Glossary Highlighting**: 
  - Uses the **`GlossaryHighlighter`** engine to perform exact match highlighting of clinical terminology.
  - Matches terms descending by character length (so compound terms like "abdominal pain" take priority over individual constituent words like "pain").
  - Enforces **Unicode-safe letter boundary constraints** (`(?<!\p{L})` and `(?!\p{L})` with the `gui` flags) to support non-ASCII characters, German umlauts, and Vietnamese diacritics flawlessly, while preventing partial word corruption (e.g. matching "ear" inside "heart").
  - Computes visible-only text lengths (omitting ANSI colors) to maintain perfect vertical column alignment in the Terminal CLI.
  - Features expanded flat coverage for **colloquial medical terms** (e.g., `puffer`, `stiff neck`, `stuffy nose`, `trouble breathing`, `runny nose`) matching natural patient speech.
- **Interactive Web Interface**:
  - Premium, modern frontend built with **glassmorphism aesthetics**.
  - Renders speech bubbles live and dynamically injects `<mark class="glossary-highlight">` tags around clinical terms.
  - Leverages a custom **`data-raw` attribute string stream pattern** to run highlights instantly in real-time on every incoming audio text chunk without HTML tag pollution or streaming timing race conditions.
  - Leverages animated, sliding tooltips on hover to display medical details, descriptions, and translation mappings case-insensitively.
  - Includes an **on-demand "Reload Glossary" button** in the sidebar to refresh glossary terms from disk instantly without reloading the page or restarting the FastAPI web server.
  - **Simultaneous Split-View Dashboards (`nurse.html` & `patient.html`)**: Support for parallel, state-synchronized multi-client interfaces tailored for clinicians and patients. Employs a robust client-side turn finalizer that splits consecutive utterances into distinct chronological speech bubbles on speaker swap, bypassing long VAD delays.
  - **Single-Tab Unified Presentation Console**: Hosted on `presentation.html` as a single parent frame. This allows presenters to seamlessly share both audio channels natively over Google Meet.
- **Unified Configuration Registry**: Uses a single central config file (`demo/interpreter_config.json`) with universally loaded default keys (such as `chunk_ms`, model name overrides, and default clinical preset mappings) to guarantee configuration parity between the Web Server and command-line execution modes.

---

## Technical Architecture

The codebase is organized as follows:

```text
├── live_translate_demo.py     # Backward-compatible forwarding wrapper to demo/web_server.py --cli
├── demo/                     # Dedicated web server & front-end assets package
│   ├── web_server.py         # FastAPI backend & unified CLI / server engine
│   ├── interpreter_config.json # Centralized JSON configuration file with presets & parameter defaults
│   └── web/                  # Glassmorphic call monitor dashboard (main.js, style.css, index.html)
├── import_glossary.py        # Polite, idempotent glossary scraper & pre-translation pipeline
├── generate_simultaneous_audio.py # Dynamic, programmatic multi-lingual Text-to-Speech stereo audio scenario compiler
├── glossary_highlighter.py   # Core match-and-highlight engine (CLI and HTML outputs)
├── glossary/                 # Local JSON database (`glossary.json`) and CSV exports
├── samples/                  # Stereo audio presets (.wav) and dialog scripts (.json) under scripts/
├── utils/                    # Developer helper utilities
│   ├── evaluate_pacing_impact.py # Side-by-side performance CLI pacing and latency comparison utility
│   ├── test_prewarming_sandbox.py # Self-contained WebSocket pre-warming keep-alive demonstration tool
│   └── list_vertex_models.py # List available GenAI models
├── tests/                    # Robust test suite covering highlighter, server endpoints, and scraping state
```

---

## Prerequisites & Installation

1. **Python**: Ensure you have Python 3.13+ installed.
2. **Environment & Dependency Manager**: Use **`uv`** (strictly recommended).
3. **Google Cloud SDK (`gcloud`)**: Installed, authenticated, and configured:
   ```bash
   gcloud auth application-default login
   ```
4. **Environment Variables**: Copy `env.example` to `.env` and set your GCP Project ID and API keys:
   ```bash
   PROJECT_ID="your-gcp-project-id"
   GEMINI_API_KEY="your-gemini-api-key"
   ```
5. **System Dependencies**: Ensure `ffmpeg` is installed on your system path (required by `pydub` to split stereo audio).

---

## Running the Clinical Demos

### 1. High-Fidelity CLI Simulator
You can run the live dual-channel terminal interpreter with real-time audio playback, side-by-side columnar layouts, and terminology highlighting in one command. All CLI commands automatically fetch settings from the centralized `demo/interpreter_config.json` while allowing full argument overrides:
```bash
# Run Spanish medical preset with real-time status columns
uv run live_translate_demo.py --preset spanish --stats

# Run German medical preset
uv run live_translate_demo.py --preset german --stats

# Run Vietnamese medical preset with custom 40ms audio chunks
uv run live_translate_demo.py --preset vietnamese --chunk-ms 40 --stats
```

Under the hood, `live_translate_demo.py` is a forwarding stub delegating parameters to the unified backend engine:
```bash
uv run demo/web_server.py --cli --preset spanish --stats
```

### 2. Premium Interactive Web UI
Launch the local web server to run the interpreter inside an interactive browser UI:
```bash
PYTHONPATH=. uv run python demo/web_server.py
```
1. Open `http://localhost:8000` in your web browser.
2. Select a language preset (German, Spanish, or Vietnamese) from the dropdown.
3. Click **Start Translation** to watch the real-time speech bubbles and hover over highlighted medical terms to view glassmorphic tooltips in action!

---

## ⚡ Pacing and Latency Performance Tuning

Pacing adjustments can occasionally impact streaming response times or audio smooth-flow. To make sure you can safely experiment and measure changes without risk:

### 1. Run Side-by-Side Pacing Comparisons
We provide a dedicated performance evaluation utility to test the impact of low-latency chunks (40ms) and active buffer clearances vs. legacy simple pacing:

```bash
# Run the newly optimized configuration profile (40ms, paced turn-holding)
uv run utils/evaluate_pacing_impact.py --profile optimized

# Run the legacy stable configuration profile (100ms, simple interval pacing)
uv run utils/evaluate_pacing_impact.py --profile legacy
```

### 2. Revert to Stable Settings instantly
If you evaluate both and decide the original stable configuration performs better, you can easily roll back with a single command:
```bash
uv run utils/evaluate_pacing_impact.py --restore-stable
```
This instantly resets `demo/interpreter_config.json` to 100ms chunks and simple pacing.

---

## 📡 WebSocket Pre-Warming & Model Preloading
To bypass connection cold-starts and establish ready-state parallel Live sessions, we support an engineering-grade pre-warming technique.

### 1. Production Integration inside the Web Server
When both Nurse and Patient dashboards are open, the FastAPI server dynamically spins up parallel Live Translate connections to Gemini in the background. 
* **Keep-Alive Loop**: To prevent gateway timeouts or idle connection drops, the server streams sparse digital silence frames (`b'\x00' * 1280` representing a 40ms frame) at a precise 2.5-second interval during idle standby periods.
* **Instant Hot-Standby Adoption**: When the Nurse starts the call, the active microphone stream instantly adopts the pre-connected hot sockets with zero handshake delay (<10ms swap latency).
* **Robust Fail-Safe**: If pre-warming is disabled (via `--no-prewarm` CLI flag or `"enable_prewarming": false` configuration) or if connection setups are interrupted, the state machine automatically falls back to standard on-demand connection handshakes.
* **UI Status Badges**: High-fidelity, colored status indicators are embedded in both Nurse and Patient headers to display the current state in real-time:
  - 🔘 `Standby: Off` (Pre-warming inactive/disabled)
  - 🟡 `Standby: Pre-warming...` (Connecting live sessions in the background)
  - 🟢 `Standby: Hot & Ready` (Hot pre-warmed sockets established and waiting)

### 2. Developer Sandbox CLI
You can safely demonstrate and verify this architecture inside a fully isolated developer sandbox script **without running the web server**:

```bash
uv run utils/test_prewarming_sandbox.py
```

The sandbox will:
1. Establish a background WebSocket connection handshake.
2. Keep the channel "hot" for 15 seconds by streaming sparse digital silence frames (`b'\x00'`) every 2.5 seconds (VAD-safe keep-alives).
3. Instantly swap a synthetic audio voice stream onto the hot channel.
4. Measure and print the first-token response latency to prove sub-second responsiveness.

---

## Dynamic Session Recycling Architecture (What Worked for Gemini 3.1)

Under **Gemini 3.1 Flash Live** (`gemini-3.1-flash-live-preview`), sending multiple speech-to-speech turns down a single WebSocket connection results in an internal server-side freeze, leading to silent GFE proxy drops and TCP keepalive timeouts on subsequent turns. We resolved this by implementing an **asynchronous background session-recycling pattern** inside the FastAPI backend.

### Architecture Highlights

- **The `ManagedSession` Context-Wrapper**: Encapsulates connection state and pre-establishes a fresh WebSocket connection asynchronously in the background. Setup takes ~1.0s and is initiated pre-emptively so connections are hot and ready before the user speaks.
- **Dynamic Connection Resolution**: Adapts the `safe_send_realtime_input` helper to extract active sockets on-the-fly from managed objects, dropping input packets safely if a recycle is currently in progress.
- **Continuously Resilient Receivers**: Receiver loops (`receive_p_to_n` and `receive_n_to_p`) run as continuous `while True` blocks. They catch `Normal Closure (1000)` exceptions when a session is closed/recycled, sleep briefly, and re-bind to the active session instantly without dropping data.
- **Non-Blocking Background Warmup**: Immediately upon a turn completing, the sender loop triggers a background warmup task to pre-warm the finished speaker's session:
  ```python
  asyncio.create_task(managed_p_to_n.connect())
  ```
  This warmup occurs during the other speaker's monologue or during natural dialogue transitions, maintaining **zero user-visible latency**.

### Independent Recycling Diagnostics
To verify this recycling pattern independently without running the full web server, you can run the simulated clinical multi-turn script:
```bash
uv run scratch/test_single_session.py
```

---

## Polite Glossary Scraper & Ingestion Pipeline

To support customized dictionaries and speech adaptations, the `import_glossary.py` scraper ingests clinical terminology from HealthDirect Australia across four main directories:

1. **Medicines Page:** [https://www.healthdirect.gov.au/medicines](https://www.healthdirect.gov.au/medicines)
2. **Conditions Directory:** [https://www.healthdirect.gov.au/health-topics/conditions](https://www.healthdirect.gov.au/health-topics/conditions)
3. **Symptoms Directory:** [https://www.healthdirect.gov.au/health-topics/symptoms](https://www.healthdirect.gov.au/health-topics/symptoms)
4. **Procedures Directory:** [https://www.healthdirect.gov.au/health-topics/procedures](https://www.healthdirect.gov.au/health-topics/procedures)

### Command-line Parameters

| Parameter | Alias | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--scrape` | `-s` | `str` | `None` | The HealthDirect directory URL to parse and crawl. |
| `--delay` | `-d` | `float` | `1.0` | Politeness sleep delay in seconds between sequential HTTP requests. |
| `--force` | `-f` | `flag`| `False` | Bypasses `scrape_state.json` and forces a fresh scrape. |
| `--state-file`| - | `str` | `glossary/scrape_state.json` | Path to the scraper's completed subpage cache file. |
| `--max-letters`| `--max` / `-m`| `int` | `None` | Limit directory scraping to a random sample of alphabetical letters. |
| `--limit-terms`| `--limit` / `-l`| `int` | `None` | Max terms to ingest from the crawl. |
| `--ground` | `-g` | `flag`| `False` | Trigger automated translation validation & Google Search grounding. |
| `--add-language`| `--al`| `str` | `None` | Add and translate existing terms to a new language (Format: Name=code, e.g. German=de) without re-scraping. |

### Scraper Execution Examples

```bash
# Polite dry-run: Crawl 2 random alphabetical sections of the Medicines directory with a 2-second politeness delay
uv run import_glossary.py --scrape "https://www.healthdirect.gov.au/medicines" --max-letters 2 --delay 2.0

# Full Resumable Crawl with Spanish/Vietnamese Translation & Search Grounding
uv run import_glossary.py --scrape "https://www.healthdirect.gov.au/health-topics/symptoms" --ground

# Add and translate all existing terms to a new language (e.g., German) on-demand, without re-scraping
uv run import_glossary.py --add-language "German=de"
```

---

## Running Automated Tests

All functionality is backed by a comprehensive unit and integration testing suite. To execute the tests offline (mocked from actual network calls):
```bash
uv run pytest
```
