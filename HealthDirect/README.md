# Real-Time Bilingual Medical Interpreter (HealthDirect Experiment)

This project is a high-fidelity, real-time bidirectional bilingual interpreter designed for clinical interactions (such as a call between a non-English-speaking patient and a HealthDirect nurse). It utilizes the **Gemini Live API** to translate multi-channel audio stream inputs in real-time, matching clinical terms against a customized, scraped dictionary and rendering highlights dynamically in both a dual-column terminal CLI and an interactive web interface.

---

## Key Features

- **Real-Time Bidirectional Translation**: Establishes dual parallel **Gemini Live API WebSocket** streams to translate patient speech (e.g., German, Spanish, Vietnamese) to English and clinician speech (English) to the patient's language concurrently.
- **Stereo Channel Splitting**: Loads stereo `.wav` audio files and separates them into independent mono feeds—the Left channel represents the Patient (foreign language) and the Right channel represents the Nurse (English).
- **Clinical Glossary Highlighting**: 
  - Uses the **`GlossaryHighlighter`** engine to perform exact match highlighting of clinical terminology.
  - Matches terms descending by character length (so compound terms like "abdominal pain" take priority over individual constituent words like "pain").
  - Enforces **Unicode-safe letter boundary constraints** (`(?<!\p{L})` and `(?!\p{L})` with the `gui` flags) to support non-ASCII characters, German umlauts, and Vietnamese diacritics flawlessly, while preventing partial word corruption (e.g. matching "ear" inside "heart").
  - Computes visible-only text lengths (omitting ANSI colors) to maintain perfect vertical column alignment in the Terminal CLI.
- **Interactive Web Interface**:
  - Premium, modern frontend built with **glassmorphism aesthetics**.
  - Renders speech bubbles live and dynamically injects `<mark class="glossary-highlight">` tags around clinical terms.
  - Leverages a custom **`data-raw` attribute string stream pattern** to run highlights instantly in real-time on every incoming audio text chunk without HTML tag pollution or streaming timing race conditions.
  - Leverages animated, sliding tooltips on hover to display medical details, descriptions, and translation mappings case-insensitively.
- **Dynamic WebSocket Connection Priming & System Instructions**:
  - Dynamically loads, filters, and formats active glossary terms from `dictionary/glossary.json` into a token-efficient key-value list on connection start.
  - Assembles highly structured system prompts enforcing a professional clinical persona and strict compliance with Australian medical spelling and nomenclature standards (e.g., `paracetamol` over `acetaminophen`, `Emergency Department` over `ER`, and Commonwealth spellings like `paediatric`, `haematology`, `gastroenteritis`).
  - Primes both parallel Patient-to-Nurse and Nurse-to-Patient Gemini Live Translate channels as a `system_instruction` parameter in the initial connection config handshakes (`LiveConnectConfig`).
- **Polite & Idempotent Glossary Scraper**:
  - A robust terminology collector (`import_glossary.py`) designed to ingest clinical lists from HealthDirect Australia.
  - **Robots.txt Adherence**: Dynamically fetches and parses the target domain's `robots.txt` using standard `urllib.robotparser` to guarantee absolute crawler compliance.
  - **Idempotency & Resilience**: Progressively persists successfully crawled subpages into `dictionary/scrape_state.json`. If a run is interrupted or times out, subsequent runs skip completed URLs, making crawls resumable.
  - **Politeness Delay**: Respects target hosts by applying a user-configurable sleep delay (`--delay` / `-d`, defaulting to `1.0s`) between sequential requests.

---

## Technical Architecture

The codebase is organized as follows:

```text
├── glossary_highlighter.py   # Core match-and-highlight engine (CLI and HTML outputs)
├── live_translate_demo.py     # High-fidelity double-column Terminal CLI interpreter simulator
├── web_server.py             # FastAPI backend coordinating audio streams, holds, and glossary APIs
├── web/                      # Glassmorphic web client (main.js, style.css, index.html)
├── import_glossary.py        # Polite, idempotent glossary scraper & pre-translation pipeline
├── generate_bilingual_audio.py# Google Cloud TTS script to generate dual-channel stereo test audio
├── samples/                  # Stereo audio presets (.wav) for German, Spanish, and Vietnamese
├── dictionary/               # Local JSON database (`glossary.json`) and CSV exports
└── tests/                    # Robust test suite covering highlighter, server endpoints, and scraping state
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
Run the live terminal interpreter with real-time audio playback, double-column turn-taking layouts, and glossary highlighting:
```bash
# Run the Spanish PRESENTS preset
uv run live_translate_demo.py --preset spanish

# Run the GermanPRESENTS preset
uv run live_translate_demo.py --preset german

# Run the Vietnamese PRESENTS preset
uv run live_translate_demo.py --preset vietnamese
```

### 2. Premium Interactive Web UI
Launch the local web server to run the interpreter inside an interactive browser UI:
```bash
uv run python web_server.py
```
1. Open `http://localhost:8000` in your web browser.
2. Select a language preset (German, Spanish, or Vietnamese) from the dropdown.
3. Click **Start Translation** to watch the real-time speech bubbles and hover over highlighted medical terms to view glassmorphic tooltips in action!

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
| `--state-file`| - | `str` | `dictionary/scrape_state.json` | Path to the scraper's completed subpage cache file. |
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
