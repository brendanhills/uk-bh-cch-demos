import os
import json
import pytest
from unittest.mock import patch
import argparse

# We import the config and parser utilities from web_server.py
# Since they do not exist yet, this will initially fail (Red Phase).
try:
    from demo.web_server import load_config, parse_args
except ImportError:
    load_config = None
    parse_args = None


def test_import_exists():
    """Asserts that load_config and parse_args are successfully imported."""
    assert load_config is not None, "load_config function must be implemented in demo/web_server.py"
    assert parse_args is not None, "parse_args function must be implemented in demo/web_server.py"


def test_load_default_config(tmp_path):
    """Verifies that load_config correctly resolves and loads the JSON configuration file."""
    test_config = {
        "model_name": "gemini-3.5-live-translate-preview",
        "chunk_ms": 40,
        "pacing_mode": "paced",
        "presets": {
            "german": {
                "file": "samples/de_fever_session.wav",
                "code": "de",
                "language": "German"
            }
        }
    }
    
    config_file = tmp_path / "interpreter_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)
        
    loaded = load_config(str(config_file))
    assert loaded["model_name"] == "gemini-3.5-live-translate-preview"
    assert loaded["chunk_ms"] == 40
    assert "german" in loaded["presets"]


def test_cli_parsing_defaults(tmp_path):
    """Verifies that parse_args uses values from the config file as defaults when no overrides are given."""
    test_config = {
        "model_name": "gemini-3.5-live-translate-preview",
        "chunk_ms": 40,
        "pacing_mode": "paced",
        "enable_playback": False,
        "presets": {}
    }
    
    config_file = tmp_path / "interpreter_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)
        
    # We call parse_args passing only ['--cli', '--config', str(config_file)]
    # All other arguments should fall back to config file defaults
    parsed = parse_args(["--cli", "--config", str(config_file)])
    assert parsed.cli is True
    assert parsed.model == "gemini-3.5-live-translate-preview"
    assert parsed.chunk_ms == 40
    assert parsed.pacing == "paced"
    assert parsed.playback is False


def test_cli_parsing_overrides(tmp_path):
    """Verifies that command-line overrides take precedence over config file defaults."""
    test_config = {
        "model_name": "gemini-3.5-live-translate-preview",
        "chunk_ms": 40,
        "pacing_mode": "paced",
        "enable_playback": False,
        "presets": {}
    }
    
    config_file = tmp_path / "interpreter_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f)
        
    # Command-line arguments explicitly overriding defaults
    parsed = parse_args([
        "--cli",
        "--config", str(config_file),
        "--model", "gemini-3.0-preview",
        "--chunk-ms", "100",
        "--pacing", "simple",
        "--playback"
    ])
    
    assert parsed.cli is True
    assert parsed.model == "gemini-3.0-preview"
    assert parsed.chunk_ms == 100
    assert parsed.pacing == "simple"
    assert parsed.playback is True


def test_chunk_size_calculations():
    """Verifies that calculate_chunk_size calculates correct byte lengths for 16kHz 16-bit mono PCM."""
    # Importing calculate_chunk_size from web_server.py
    try:
        from demo.web_server import calculate_chunk_size
    except ImportError:
        calculate_chunk_size = None
        
    assert calculate_chunk_size is not None, "calculate_chunk_size must be implemented in demo/web_server.py"
    
    # 40ms: 16000 * 1 * 2 * 0.04 = 1280 bytes
    assert calculate_chunk_size(40) == 1280
    # 20ms: 16000 * 1 * 2 * 0.02 = 640 bytes
    assert calculate_chunk_size(20) == 640
    # 100ms: 16000 * 1 * 2 * 0.10 = 3200 bytes
    assert calculate_chunk_size(100) == 3200


def test_interruption_buffer_clearance():
    """Verifies that an interruption event resets/clears local playback and streaming buffers."""
    try:
        from demo.web_server import clear_active_buffers
    except ImportError:
        clear_active_buffers = None
        
    assert clear_active_buffers is not None, "clear_active_buffers must be implemented in demo/web_server.py"
    
    # Create test list/queue structures to simulate buffers
    test_playback_queue = [b"chunk1", b"chunk2"]
    test_stream_queue = [b"chunk3", b"chunk4"]
    
    clear_active_buffers(test_playback_queue, test_stream_queue)
    
    # Assert buffers are fully cleared/empty
    assert len(test_playback_queue) == 0
    assert len(test_stream_queue) == 0


def test_run_cli_exists():
    """Verifies that the main CLI entry point function run_cli exists and can be imported."""
    try:
        from demo.web_server import run_cli
    except ImportError:
        run_cli = None
        
    assert run_cli is not None, "run_cli function must be implemented in demo/web_server.py to drive the CLI mode"


