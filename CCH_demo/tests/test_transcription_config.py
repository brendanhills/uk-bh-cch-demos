"""Unit test verifying AudioTranscriptionConfig includes Arabic ('ar') language hints (BUG-36)."""

import pytest
from google.genai import types


def test_arabic_audio_transcription_language_hints():
    """Verify input audio transcription config supports both English and Arabic speech (BUG-36)."""
    input_cfg = types.AudioTranscriptionConfig(
        language_hints=types.LanguageHints(language_codes=["en-AU", "ar"])
    )
    assert "en-AU" in input_cfg.language_hints.language_codes
    assert "ar" in input_cfg.language_hints.language_codes
