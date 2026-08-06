# Specification - Verify and benchmark the existing transcription application

## Overview
This track aims to verify that the duplicated transcription codebase runs successfully in the new workspace environment (`HealthDirect`) and to benchmark its current performance (latency, accuracy, and speaker attribution). This establishes a solid, working baseline before introducing the translation features.

## Scope & Objectives
1. **Dependency Integrity:** Confirm all Python dependencies resolve and compile correctly under Python 3.13 using `uv`.
2. **Test Baseline:** Run the existing test suite to verify that all unit/integration tests pass.
3. **End-to-End Simulation:** Execute the transcription demo scripts (`parallel_transcribe.py`, `two_channel_transcribe_v2.py`) to confirm real-time streaming and Terminal UI rendering.
4. **Performance Benchmarking:** Collect initial latency and attribution metrics using comparison scripts to use as a baseline for future translation benchmarks.

## Verification Criteria
- All automated tests run and pass without errors.
- End-to-end transcription runs without exception.
- Speaker attribution colors and VAD pinning function in the CLI.
- Latency and performance statistics are successfully gathered.
