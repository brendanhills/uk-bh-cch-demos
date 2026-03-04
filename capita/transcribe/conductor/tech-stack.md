# Tech Stack

This document outlines the core technologies and libraries used in the Real-Time Transcription Simulator.

## 1. Language and Runtime
- **Python 3.13+**: The core programming language, chosen for its strong ecosystem of audio processing and GCP client libraries.
- **uv**: The preferred package and project manager for fast, reproducible dependency resolution.

## 2. Cloud Infrastructure (Google Cloud Platform)
- **Speech-to-Text API (V2)**: The primary engine for multi-channel, real-time transcription. V2 is selected for its enhanced features and performance, including specialized support for **Chirp-3**.
- **Speech-to-Text API (V1)**: Maintained for legacy support and comparison, specifically for AI-driven diarization on mono files.
- **Google Cloud Storage (GCS)**: Used for storing and streaming the source audio files.

## 3. Audio Processing
- **pydub**: Used for high-level audio manipulation (loading, normalization, segmenting).
- **ffmpeg-python**: Provides the underlying decoding and encoding capabilities required by `pydub`.
- **audioop-lts**: Used for low-level, real-time audio operations such as channel down-mixing.

## 4. Development & Testing
- **pytest**: The primary testing framework.
- **pytest-asyncio**: Required for testing the asynchronous STT streaming logic.
- **dotenv**: Manages environment-specific configuration (Project IDs, Recognizers) via `.env` files.

## 5. UI & CLI
- **ANSI Escape Codes**: Leveraged for real-time terminal manipulation, including cursor movement and color rendering.
- **textwrap**: Used for consistent columnar formatting in various terminal sizes.
