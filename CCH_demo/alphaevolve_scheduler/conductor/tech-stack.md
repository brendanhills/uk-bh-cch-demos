# Technology Stack: RCH Resource & Staff Co-Scheduling x AlphaEvolve

## Optimization Backend
- **Language:** Python
- **Core Framework:** `alphaevolve` (Direct Git installation from Google Cloud AI repository)
- **Model Policy:** Exclusively Gemini 3 or later (e.g., `gemini-3.5-flash`). Earlier generations (Gemini 1.x, 2.x) are strictly unsupported and rejected by the API as of July 2026.
- **Key Libraries:**
  - `numpy`: Numerical processing for constraints and scoring.
  - `python-dotenv`: Environment variable management.
  - `nest_asyncio`: Asynchronous execution support.
- **Environment & Dependency Manager:** `uv` (Fast, reproducible dependency resolution).

## Frontend / Dashboard
- **Architecture:** Static, single-file HTML5 Dashboard.
- **Technologies:** Vanilla HTML5, CSS3, and JavaScript (Inline, embedded within the file).
- **Network Dependency:** Strictly zero network calls at demo time. All assets and libraries must be embedded or locally served to ensure high portability and speed.

## Data Schema & Persistence
- **Static Configuration:** JSON (Defines the Phase 1 resources, staff pools, and baseline demands).
- **Evolution Traces:** JSONL (Appended in real-time by the optimization loop to drive the UI animations).

## Serving & Execution
- **Serving:** Lightweight static file serving via a Shell script (`serve.sh`), leveraging Python's built-in `http.server`.
