# Technology Stack: Cymbal Children's Hospital Assistant

## Core Runtime & Dependencies
- **Programming Language**: Python 3.10+ (managed via `uv`)
- **Package & Environment Manager**: `uv` (`pyproject.toml`)

## Backend Infrastructure
- **Web Framework**: FastAPI 0.115+
- **ASGI Server**: Uvicorn (`uvicorn[standard]`)
- **Real-Time Protocol**: WebSockets (`/ws/{user_id}/{session_id}`)

## AI & Agent Engine
- **Framework**: Google Agent Development Kit (`google-adk>=1.32.0`)
- **Live Streaming API**: Gemini Live API (`run_live` concurrent BIDI upstream/downstream queue processing)
- **Model Endpoints**: `gemini-3.1-flash-live-preview` (Gemini 3.1 Flash Live native audio BIDI streaming)

## Frontend & Client Interface
- **Architecture**: Single Page Application (FastAPI Static Files)
- **Tech Stack**: Vanilla JavaScript (ES6+), HTML5, CSS3
- **Audio Pipeline**: Web Audio API (AudioContext + Audio Worklet processor)
- **Camera Capture**: MediaDevices API (photo snapshot capture)

## Testing & Quality Assurance
- **Test Framework**: Pytest (`pytest>=8.0.0`, `pytest-asyncio>=0.24.0`)
- **Linter / Formatter**: Ruff (`target-version = "py310"`)
