import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from google.cloud import texttospeech
from generate_simultaneous_audio import (
    format_ssml_text,
    VOICE_MAPPING,
    synthesize_voice
)


def test_ssml_tag_injection_and_formatting():
    """Verifies format_ssml_text rates, pitches, breaks, and emphasis."""
    raw_text = "Guten Tag. Ich habe Kopfschmerzen, Fieber und Schmerzen."
    ssml = format_ssml_text(raw_text)
    
    assert ssml.startswith("<speak><prosody rate=\"85%\" pitch=\"-2st\">")
    assert ssml.endswith("</prosody></speak>")
    assert "<break time=\"500ms\"/>" in ssml
    
    # Verify keywords are wrapped with moderate emphasis
    assert '<emphasis level="moderate">Kopfschmerzen</emphasis>' in ssml
    assert '<emphasis level="moderate">Fieber</emphasis>' in ssml
    assert '<emphasis level="moderate">Schmerzen</emphasis>' in ssml


def test_ssml_formatting_empty_string():
    """Asserts that format_ssml_text handles empty input robustly."""
    ssml = format_ssml_text("")
    assert ssml == (
        "<speak><prosody rate=\"85%\" pitch=\"-2st\"></prosody></speak>"
    )


def test_voice_mapping_structure():
    """Ensures German, Spanish, Vietnamese, and Arabic have proper mappings."""
    languages = ["german", "spanish", "vietnamese", "arabic"]
    for lang in languages:
        assert lang in VOICE_MAPPING, f"{lang} missing from VOICE_MAPPING."
        for role in ["caller", "nurse"]:
            assert role in VOICE_MAPPING[lang], f"{role} missing for {lang}."
            config = VOICE_MAPPING[lang][role]
            assert "language_code" in config
            assert "voice_name" in config
            assert "gender" in config
            assert "fallback_voice" in config


@pytest.mark.asyncio
async def test_synthesis_fallback_mitigation():
    """Tests that if regional voice fails, fallback retry occurs."""
    with patch(
        "google.cloud.texttospeech.TextToSpeechAsyncClient"
    ) as mock_client_cls:
        mock_client = mock_client_cls.return_value
        
        # Make the first synthesis attempt raise an error
        mock_response = MagicMock()
        mock_response.audio_content = b"RIFF_MOCK_WAV_PCM_DATA_16KHZ"
        
        mock_client.synthesize_speech = AsyncMock()
        mock_client.synthesize_speech.side_effect = [
            Exception("TTS API Error: Invalid SSML schema for regional model"),
            mock_response
        ]
        
        # Call synthesize_voice and mock AudioSegment.from_file
        with patch("pydub.AudioSegment.from_file") as mock_from_file:
            mock_audio = MagicMock()
            mock_from_file.return_value = mock_audio
            
            result = await synthesize_voice(
                text="Hello",
                is_caller=True,
                preset_key="german",
                use_ssml=True
            )
            
            assert result == mock_audio
            assert mock_client.synthesize_speech.call_count == 2
            
            # Verify the second call fell back to the fallback voice
            calls = mock_client.synthesize_speech.call_args_list
            second_call_voice = calls[1].kwargs["voice"]
            target_fallback = (
                VOICE_MAPPING["german"]["caller"]["fallback_voice"]
            )
            assert second_call_voice.name == target_fallback
            
            # Verify the second call used text, not SSML
            second_call_input = calls[1].kwargs["input"]
            assert second_call_input.text == "Hello"
            assert not second_call_input.ssml
