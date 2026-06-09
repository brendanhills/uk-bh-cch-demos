# Tech Stack

This document outlines the core technologies and libraries used in the Real-Time Transcription and Translation Simulator.

## 1. Language and Runtime
- **Python 3.13+**: The core programming language, chosen for its strong ecosystem of audio processing and GCP client libraries.
- **uv**: The preferred package and project manager for fast, reproducible dependency resolution.

## 2. Cloud Infrastructure (Google Cloud Platform)
- **Speech-to-Text API (V2)**: The primary engine for multi-channel, real-time transcription, including specialized support for Chirp-3.
- **Speech-to-Text API (V1)**: Maintained for legacy support and comparison, specifically for AI-driven diarization on mono files.
- **Google Cloud Storage (GCS)**: Used for storing and streaming the source audio files.

## 3. Translation Modules and APIs (for Comparison and Evaluation)
- **Google Cloud Translation API V3 (Advanced)**: For fast, standard machine translation with custom glossaries and models.
- **Gemini API / Vertex AI (Large Language Models)**: Using LLM prompt-based translation to evaluate translation quality, nuance, and contextual accuracy compared to traditional translation.
- **Google Cloud Translation API V2 (Basic)**: Included as a baseline for basic machine translation comparison.

## 4. Audio Processing
- **pydub**: Used for high-level audio manipulation (loading, normalization, segmenting).
- **ffmpeg-python**: Provides the underlying decoding and encoding capabilities required by `pydub`.
- **audioop-lts**: Used for low-level, real-time audio operations such as channel down-mixing.

## 5. Development & Testing
- **pytest**: The primary testing framework.
- **pytest-asyncio**: Required for testing the asynchronous STT and translation streaming logic.
- **dotenv**: Manages environment-specific configuration (Project IDs, Recognizers, API Keys) via `.env` files.

## 6. UI & CLI
- **ANSI Escape Codes**: Leveraged for real-time terminal manipulation, including cursor movement and color rendering.
- **textwrap**: Used for consistent side-by-side columnar formatting in various terminal sizes (Transcription vs. Translation).
