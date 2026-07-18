#!/usr/bin/env python3
"""Tests for pre-warming configuration and CLI parsing logic.

Asserts that --no-prewarm and 'enable_prewarming' parameters are parsed
correctly and respect design-specified precedence.
"""

import pytest
from unittest.mock import patch
from demo.web_server import parse_args


def test_prewarming_defaults():
    """Verifies that pre-warming defaults to True if config is missing."""
    with patch("demo.web_server.load_config", return_value={}):
        parsed = parse_args([])
        # Since it is parsed as '--no-prewarm', the parsed attribute is 'no_prewarm'
        # if enable_prewarming is True (default), then no_prewarm defaults to False
        assert parsed.no_prewarm is False


def test_prewarming_config_loading():
    """Verifies that enable_prewarming is loaded from config file."""
    mock_config = {
        "enable_prewarming": False,
        "model_name": "gemini-3.5-live-translate-preview"
    }
    
    with patch("demo.web_server.load_config", return_value=mock_config):
        parsed = parse_args([])
        # If enable_prewarming is False in config, no_prewarm is True by default
        assert parsed.no_prewarm is True


def test_prewarming_cli_override():
    """Verifies that CLI flag --no-prewarm overrides config values."""
    mock_config = {
        "enable_prewarming": True,
        "model_name": "gemini-3.5-live-translate-preview"
    }
    
    with patch("demo.web_server.load_config", return_value=mock_config):
        # Command line explicitly overrides to disable prewarming
        parsed = parse_args(["--no-prewarm"])
        assert parsed.no_prewarm is True
