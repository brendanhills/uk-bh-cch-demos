import pytest
import asyncio
import os
from unittest.mock import MagicMock, patch
from simulate_audio import AudioStreamSimulator

@pytest.mark.asyncio
async def test_simulator_prepare_local(tmp_path):
    """Ensures simulator can prepare from a local file."""
    # Create a dummy audio file
    dummy_file = tmp_path / "test.wav"
    dummy_file.write_bytes(b"RIFF" + b"\x00" * 100) # Minimum valid-ish wave header
    
    # We need to mock AudioSegment.from_file because our dummy file is not a real audio file
    with patch("pydub.AudioSegment.from_file") as mock_from_file:
        mock_seg = MagicMock()
        mock_seg.channels = 2
        mock_seg.frame_rate = 8000
        mock_seg.set_sample_width.return_value.raw_data = b"\x00" * 16000 # 1 second of audio
        mock_from_file.return_value = mock_seg
        
        simulator = AudioStreamSimulator(str(dummy_file))
        await simulator.prepare()
        
        assert simulator.source_channels == 2
        assert simulator.sample_rate == 8000
        assert len(simulator.audio_bytes) == 16000

@pytest.mark.asyncio
async def test_simulator_stream():
    """Validates the real-time throttling of the audio stream."""
    simulator = AudioStreamSimulator("dummy.wav")
    simulator.bytes_per_sec = 16000 # 8000Hz, 1ch, 2 bytes
    simulator.source_channels = 1
    simulator.audio_bytes = b"\x00" * 8000 # 0.5 seconds of audio
    
    start_time = asyncio.get_event_loop().time()
    chunks = []
    async for chunk in simulator.stream():
        chunks.append(chunk)
        
    end_time = asyncio.get_event_loop().time()
    
    # 0.5 seconds of audio should take approx 0.5 seconds to stream
    # Chunks are 250ms, so we expect 2 chunks.
    assert len(chunks) == 2
    assert end_time - start_time >= 0.25 # At least one chunk sleep
