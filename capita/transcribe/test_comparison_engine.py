import pytest
import asyncio
import datetime
from unittest.mock import MagicMock, AsyncMock, patch
from transcribe_common import TranscriptionService, ComparisonManager, BaseTranscriptionService

@pytest.mark.asyncio
async def test_transcription_service_endpoint_selection():
    """Validates that TranscriptionService selects the correct endpoint based on model."""
    # Test with non-chirp model
    service_telephony = TranscriptionService(16000, 1, model_name="telephony")
    assert service_telephony.api_location == "us-central1" # Default GCP_LOCATION
    
    # Test with chirp model
    service_chirp = TranscriptionService(16000, 1, model_name="chirp_3")
    assert service_chirp.api_location == "us"
    assert service_chirp.CHIRP_MODE is True

@pytest.mark.asyncio
async def test_comparison_manager_distribution():
    """Ensures ComparisonManager distributes audio chunks to all registered services."""
    mock_service_1 = MagicMock(spec=TranscriptionService)
    mock_service_1.run = AsyncMock()
    mock_service_2 = MagicMock(spec=TranscriptionService)
    mock_service_2.run = AsyncMock()
    
    manager = ComparisonManager([mock_service_1, mock_service_2])
    
    async def mock_audio_stream():
        yield b"chunk1"
        yield b"chunk2"
        
    await manager.run(mock_audio_stream())
    
    # Verify that run was called on both services
    assert mock_service_1.run.called
    assert mock_service_2.run.called

def test_split_by_gaps():
    """Validates monologue splitting based on silence gaps."""
    service = BaseTranscriptionService(16000, 1)
    service.GAP_THRESHOLD = 0.5
    
    # Mock word objects with start/end offsets
    word1 = MagicMock()
    word1.word = "hello"
    word1.start_offset.total_seconds.return_value = 0.0
    word1.end_offset.total_seconds.return_value = 0.5
    
    word2 = MagicMock()
    word2.word = "world"
    word2.start_offset.total_seconds.return_value = 1.1 # Gap of 0.6s
    word2.end_offset.total_seconds.return_value = 1.6
    
    chunks = service._split_by_gaps([word1, word2], 1)
    assert len(chunks) == 2
    assert chunks[0]["text"] == "hello"
    assert chunks[1]["text"] == "world"

def test_split_by_punctuation():
    """Validates fallback sentence splitting."""
    service = BaseTranscriptionService(16000, 1)
    
    text = "Hello world. This is a test! Is it working?"
    chunks = service._split_by_punctuation(text, 1, 0.0, 3.0)
    
    assert len(chunks) == 3
    assert "Hello world." in chunks[0]["text"]
    assert "This is a test!" in chunks[1]["text"]
    assert "Is it working?" in chunks[2]["text"]
    assert chunks[0]["start"] == 0.0
    # Implementation has a small gap logic: p_end = start_sec + ((i + 0.9) * (duration / len(parts)))
    # (2 + 0.9) * (3.0 / 3) = 2.9
    assert pytest.approx(chunks[2]["end"]) == 2.9

def test_stability_buffer_ordering():
    """Ensures stability buffer releases chunks in chronological order."""
    service = BaseTranscriptionService(16000, 1)
    service.STABILITY_THRESHOLD = 1.0
    service.current_audio_time = 2.5
    service.start_time = datetime.datetime.now(datetime.timezone.utc)
    
    # Add chunks to buffer
    chunk_early = {"text": "early", "start": 0.5, "channel": 1}
    chunk_late = {"text": "late", "start": 1.2, "channel": 1}
    
    service.stability_buffer = [chunk_late, chunk_early]
    
    # We need to mock _print_in_column to avoid terminal output
    with patch.object(service, "_print_in_column"):
        service._process_stability_buffer()
        
    assert len(service.transcript_chunks) == 2
    assert service.transcript_chunks[0]["text"] == "early"
    assert service.transcript_chunks[1]["text"] == "late"
