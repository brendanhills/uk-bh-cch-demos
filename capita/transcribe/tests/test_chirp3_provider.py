import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from core.models import TranscriptionEvent
from core.chirp3_provider import Chirp3Provider
from google.cloud import speech_v2 as cs_v2

@pytest.mark.asyncio
async def test_chirp3_provider_config():
    """Verifies Chirp3Provider uses the correct specialized configuration."""
    mock_client = AsyncMock(spec=cs_v2.SpeechAsyncClient)
    
    # Mock get_recognizer to return a fake recognizer
    mock_recognizer = MagicMock()
    mock_client.get_recognizer.return_value = mock_recognizer
    
    # Mock streaming_recognize to be an async function that returns an async iterator
    async def mock_streaming_recognize(requests):
        async def response_gen():
            if False: yield # make it a generator
        return response_gen()
    mock_client.streaming_recognize.side_effect = mock_streaming_recognize

    provider = Chirp3Provider(
        client=mock_client,
        recognizer_name="projects/p/locations/us/recognizers/r",
        model="chirp-3"
    )
    
    # Mock audio generator
    async def audio_gen():
        yield b"fake audio"

    # Run the stream (it will yield nothing but we want to check the calls)
    async for _ in provider.stream(audio_gen()):
        pass

    # Verify streaming_recognize was called with correct config
    call_args = mock_client.streaming_recognize.call_args
    print(f"DEBUG: call_args={call_args}")
    requests = call_args.kwargs.get('requests') or call_args.args[0]
    
    # Get the first request which should be the config
    first_request = await anext(requests)
    config = first_request.streaming_config.config
    
    assert config.language_codes == ["auto"]
    assert config.model == "chirp-3"
    # Chirp-3 specific decoding config
    assert config.explicit_decoding_config.encoding == cs_v2.ExplicitDecodingConfig.AudioEncoding.LINEAR16
    assert config.explicit_decoding_config.sample_rate_hertz == 16000

@pytest.mark.asyncio
async def test_chirp3_provider_wordless_events():
    """Verifies Chirp3Provider handles events without word-level timestamps."""
    mock_client = AsyncMock(spec=cs_v2.SpeechAsyncClient)
    mock_recognizer = MagicMock()
    mock_client.get_recognizer.return_value = mock_recognizer
    
    # Mock a response with no words
    mock_response = MagicMock()
    mock_response.speech_event_type = 0
    result = MagicMock()
    result.is_final = True
    result.channel_tag = 1
    alt = MagicMock()
    alt.transcript = "hello world"
    alt.words = [] # Empty words
    result.alternatives = [alt]
    mock_response.results = [result]

    async def mock_streaming_recognize(requests):
        # We need to exhaust the requests generator to advance time
        async for _ in requests:
            pass
        async def response_gen():
            yield mock_response
        return response_gen()
    
    mock_client.streaming_recognize.side_effect = mock_streaming_recognize

    provider = Chirp3Provider(
        client=mock_client,
        recognizer_name="projects/p/locations/us/recognizers/r"
    )
    
    # 2 chunks of 0.5s = 1.0s total
    async def audio_gen():
        yield b"chunk1"
        yield b"chunk2"

    events = []
    async for ev in provider.stream(audio_gen(), chunk_duration_sec=0.5):
        events.append(ev)

    assert len(events) == 1
    ev = events[0]
    assert ev.text == "hello world"
    # Fallback timing (1.0 - 1.0 = 0.0)
    assert ev.start_sec == 0.0
    assert ev.end_sec == 1.0
    assert ev.words == []
