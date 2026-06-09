import pytest
import asyncio
from unittest.mock import MagicMock
from core.models import TranscriptionEvent
from core.workers import RawChannelWorker

@pytest.mark.asyncio
async def test_raw_channel_worker():
    """Ensures RawChannelWorker passes everything through immediately."""
    provider = MagicMock()
    # Mock a stream of 2 events
    events = [
        TranscriptionEvent(speaker_id=1, text="hello", start_sec=0.1, end_sec=0.2, is_final=False),
        TranscriptionEvent(speaker_id=1, text="world", start_sec=0.1, end_sec=0.5, is_final=True)
    ]
    
    async def mock_stream(*args, **kwargs):
        for e in events:
            yield e
            
    provider.stream = mock_stream
    
    worker = RawChannelWorker(provider, channel_id=1)
    output_q = asyncio.Queue()
    
    # We don't need audio_gen for this test
    await worker.run(None, output_q, chunk_duration_sec=0.1)
    
    assert output_q.qsize() == 3
    assert (await output_q.get()).text == "hello"
    assert (await output_q.get()).text == "world"
    assert (await output_q.get()) is None
