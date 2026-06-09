import pytest
import asyncio
import audioop
from unittest.mock import MagicMock, AsyncMock
from core.utils import run_broadcaster

@pytest.mark.asyncio
async def test_run_broadcaster_two_channel():
    """Verifies broadcaster correctly feeds a single queue and advances engine clock."""
    simulator = MagicMock()
    # Mock a stream of 4 chunks, each representing 0.1s
    chunks = [b"\x01" * 400, b"\x02" * 400, b"\x03" * 400, b"\x04" * 400]
    
    async def mock_stream(duration=None, chunk_duration_sec=0.1):
        for c in chunks:
            yield c
            
    simulator.stream = mock_stream
    
    engine = MagicMock()
    audio_q = asyncio.Queue()
    
    await run_broadcaster(simulator, engine, audio_q, duration=None, chunk_size=0.1)
    
    # 1. Check engine clock updates
    # Should be called 4 times: 0.1, 0.2, 0.3, 0.4
    assert engine.set_audio_time.call_count == 4
    engine.set_audio_time.assert_any_call(0.1)
    engine.set_audio_time.assert_any_call(0.4)
    
    # 2. Check queue contents
    assert audio_q.qsize() == 5 # 4 chunks + None (EOF)
    for i in range(4):
        item = await audio_q.get()
        assert item == chunks[i]
    assert await audio_q.get() is None

@pytest.mark.asyncio
async def test_run_broadcaster_parallel():
    """Verifies broadcaster correctly splits stereo into mono for parallel workers."""
    simulator = MagicMock()
    
    # Create 4 chunks of stereo audio (L, R, L, R...)
    # 2 channels, 2 bytes per sample -> 4 bytes per frame
    # We'll make L=1, R=2
    stereo_chunk = bytes([1, 0, 2, 0] * 100) # 100 frames
    chunks = [stereo_chunk] * 4
    
    async def mock_stream(duration=None, chunk_duration_sec=0.1):
        for c in chunks:
            yield c
            
    simulator.stream = mock_stream
    
    engine = MagicMock()
    q1, q2 = asyncio.Queue(), asyncio.Queue()
    
    await run_broadcaster(simulator, engine, [q1, q2], duration=None, chunk_size=0.1)
    
    # 1. Check engine clock
    assert engine.set_audio_time.call_count == 4
    
    # 2. Check splits
    # Left channel (q1) should be all 1s
    l_item = await q1.get()
    assert l_item == bytes([1, 0] * 100)
    
    # Right channel (q2) should be all 2s
    r_item = await q2.get()
    assert r_item == bytes([2, 0] * 100)
    
    # Check EOF
    assert q1.qsize() == 4 # 3 chunks remaining + None
    while q1.qsize() > 1: await q1.get()
    assert await q1.get() is None
    
    assert q2.qsize() == 4
    while q2.qsize() > 1: await q2.get()
    assert await q2.get() is None
