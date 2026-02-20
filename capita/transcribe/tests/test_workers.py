import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from core.models import TranscriptionEvent
from core.workers import RawChannelWorker, StabilizedChannelWorker

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

@pytest.mark.asyncio
async def test_stabilized_channel_worker_buffering():
    """Verifies StabilizedChannelWorker buffers final results until clock advances."""
    provider = MagicMock()
    # Final event ending at 1.0s
    final_ev = TranscriptionEvent(speaker_id=1, text="buffered", start_sec=0.5, end_sec=1.0, is_final=True)
    
    async def mock_stream(*args, **kwargs):
        yield final_ev
            
    provider.stream = mock_stream
    
    # Threshold 1.0s -> needs clock > 2.0s to release
    worker = StabilizedChannelWorker(provider, channel_id=1, stability_threshold=1.0)
    output_q = asyncio.Queue()
    
    # Run the worker in a task so we can manipulate time
    run_task = asyncio.create_task(worker.run(None, output_q, chunk_duration_sec=0.1))
    
    # 1. Initially, clock is 0.0. Queue should be empty of transcripts, but contain None if finished.
    await asyncio.sleep(0.1)
    assert output_q.qsize() == 1
    assert (await output_q.get()) is None
    
    # 2. Advance clock to 1.5s. Still not stable (1.0 + 1.0 = 2.0 needed).
    worker.update_time(1.5)
    await worker._flush_stable(output_q) # Manually trigger flush for test
    assert output_q.qsize() == 0
    
    # 3. Advance clock to 2.1s. Should release.
    worker.update_time(2.1)
    await worker._flush_stable(output_q)
    assert output_q.qsize() == 1
    assert (await output_q.get()).text == "buffered"

@pytest.mark.asyncio
async def test_stabilized_channel_worker_gap_splitting():
    """Verifies worker splits a single long result into turns locally."""
    provider = MagicMock()
    # A long result with a gap between 1.0 and 2.0
    long_ev = TranscriptionEvent(
        speaker_id=1, text="part one part two", start_sec=0.0, end_sec=3.0, is_final=True,
        words=[
            {"word": "part", "start": 0.0, "end": 0.5},
            {"word": "one", "start": 0.5, "end": 1.0},
            {"word": "part", "start": 2.0, "end": 2.5},
            {"word": "two", "start": 2.5, "end": 3.0}
        ]
    )
    
    async def mock_stream(*args, **kwargs):
        yield long_ev
            
    provider.stream = mock_stream
    
    worker = StabilizedChannelWorker(provider, channel_id=1, gap_threshold=0.5)
    output_q = asyncio.Queue()
    
    # Force release
    worker.current_audio_time = 10.0
    await worker.run(None, output_q, chunk_duration_sec=0.1)
    
    # Should be 2 events now + None
    assert output_q.qsize() == 3
    ev1 = await output_q.get()
    ev2 = await output_q.get()
    ev3 = await output_q.get()
    
    assert ev1.text == "part one"
    assert ev2.text == "part two"
    assert ev3 is None
    assert ev1.start_sec == 0.0
    assert ev2.start_sec == 2.0
