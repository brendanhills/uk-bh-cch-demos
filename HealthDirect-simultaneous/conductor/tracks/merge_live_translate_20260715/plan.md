# Implementation Plan: Merge Live Translate Demo into Web Server (`merge_live_translate_20260715`)

## Phase 1: Configuration and CLI Parsing

- [x] Task: TDD - Write failing tests for Configuration loading and CLI parsing
    - [x] Create test `tests/test_merge_cli_config.py` to verify that `demo/interpreter_config.json` loads correctly.
    - [x] Write unit tests to check CLI argument parsing in `demo/web_server.py`, including default fallbacks from the config file and argument overrides.
    - [x] Assert that the tests fail as expected (Red Phase).
- [x] Task: Create centralized configuration file `demo/interpreter_config.json`
    - [x] Define `demo/interpreter_config.json` containing model names, chunk size (40ms), default flags, pacing parameters, and preset file/language options.
    - [x] Update `.gitignore` to ensure that `.env` remains ignored while `demo/interpreter_config.json` is tracked.
- [x] Task: Implement configuration and CLI parsing in `demo/web_server.py`
    - [x] Implement configuration loader using standard `json` and path resolution.
    - [x] Implement CLI argument parsing utilizing standard `argparse`. If `--cli` is provided, enable CLI mode; otherwise, default to Server mode.
    - [x] Ensure that CLI overrides correctly take precedence over the central configuration defaults.
- [x] Task: Verify Phase 1 tests pass and refactor
    - [x] Run `pytest tests/test_merge_cli_config.py` and confirm all tests pass (Green Phase).
    - [x] Refactor parser and loader logic for clarity, and re-run checks.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Configuration and CLI Parsing' (Protocol in workflow.md)

## Phase 2: Core Refactoring and Best Practices

- [x] Task: TDD - Write failing tests for chunk configuration and interruption handling
    - [x] Add tests in `tests/test_merge_cli_config.py verifying that chunk size (e.g. 40ms, 20ms) correctly maps to the expected byte lengths.
    - [x] Write tests to verify that receiving an `interrupted: true` event in the live connection handler triggers immediate audio buffer clearance.
    - [x] Assert that the tests fail as expected (Red Phase).
- [x] Task: Refactor web server streaming loop to support configurable chunks and best practices
    - [x] Modify the audio chunking logic in `demo/web_server.py` to dynamically calculate chunk sizes based on the loaded `chunk_ms` configuration.
    - [x] Ensure the streaming loops for both Server and CLI modes utilize these precise, low-latency chunks (defaulting to 40ms).
- [x] Task: Integrate Best Practices (Interruption & Session Signals)
    - [x] Implement interruption handling: when `server_content.interrupted` is true, immediately clear active playback and streaming queues.
    - [x] Add explicit logging and handlers for `GoAway` messages and `generationComplete` signals in connection sessions.
    - [x] Append `RESPOND IN {OUTPUT_LANGUAGE}. YOU MUST RESPOND UNMISTAKABLY IN {OUTPUT_LANGUAGE}.` to target language system instructions.
- [x] Task: Verify Phase 2 tests pass and refactor
    - [x] Run the test suite and confirm that all tests pass (Green Phase).
    - [x] Ensure no performance or latency regression in browser-side WebSocket streaming.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Refactoring and Best Practices' (Protocol in workflow.md)

## Phase 3: CLI Integration and Consolidation

- [x] Task: TDD - Write failing tests for CLI execution mode
    - [x] Write tests that execute `demo/web_server.py` in CLI mode using subprocess/mocking to verify it starts, loads a preset, and generates translated raw PCM outputs in `output/`.
    - [x] Assert that the tests fail as expected (Red Phase).
- [x] Task: Implement CLI Mode Runner and Presentation Logic
    - [x] Port terminal-only UI formatting, side-by-side columnar rendering, and colored ANSI output from `live_translate_demo.py` into the CLI execution path of `demo/web_server.py`.
    - [x] Integrate optional pacing toggle (`--pacing simple` vs `--pacing paced`).
- [x] Task: Implement local audio playback, stats logging, and file outputs
    - [x] Write translated audio to PCM/WAV output files in the `output/` directory.
    - [x] Add optional local speaker playback if `pyaudio` or `simpleaudio` is present.
    - [x] Implement a stats tracker (`--stats`) to print real-time frame stats, latency metrics, and throughput.
- [x] Task: Verify Phase 3 tests pass and consolidate code
    - [x] Run the test suite and verify everything passes (Green Phase).
    - [x] Replace the root-level `live_translate_demo.py` with a lean wrapper script that forwards calls directly to `demo/web_server.py --cli`.
- [x] Task: Conductor - User Manual Verification 'Phase 3: CLI Integration and Consolidation' (Protocol in workflow.md)
