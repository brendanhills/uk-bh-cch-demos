import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
from simulate_audio import AudioStreamSimulator
from mono_transcribe_v1 import MonoTranscriptionServiceV1
from two_channel_transcribe_v2 import UnifiedTwoChannelService
from transcribe import TranscriptionService as LegacyService

TEST_URI = "gs://uk-bh-experiments-argolis-us/capita/4507.mp3"

@pytest.mark.asyncio
@patch("asyncio.sleep", return_value=None) # Speed up playback
async def test_mono_v1_integration(mock_sleep):
    """Ensures V1 Mono can process audio."""
    simulator = AudioStreamSimulator(TEST_URI, force_mono=True)
    await simulator.prepare()
    
    # Limit bytes to approx 10 seconds for faster test
    bytes_limit = simulator.bytes_per_sec * 10
    simulator.audio_bytes = simulator.audio_bytes[:bytes_limit]
    
    service = MonoTranscriptionServiceV1(simulator.sample_rate, simulator.channels)
    
    try:
        await asyncio.wait_for(service.run(simulator.stream()), timeout=120)
    except asyncio.TimeoutError:
        pytest.fail("V1 Integration timed out")

    assert len(service.transcript_chunks) > 0, "V1 produced no transcript chunks"
    print(f"\nV1 Test Success: {len(service.transcript_chunks)} chunks captured.")

@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["low_latency", "readability"])
@patch("asyncio.sleep", return_value=None)
async def test_stereo_v2_integration(mock_sleep, mode):
    """Ensures Unified Stereo (V2) can process audio in both modes."""
    simulator = AudioStreamSimulator(TEST_URI, force_mono=False)
    await simulator.prepare()
    
    # Limit to 10 seconds
    bytes_limit = simulator.bytes_per_sec * 10
    simulator.audio_bytes = simulator.audio_bytes[:bytes_limit]
    
    service = UnifiedTwoChannelService(simulator.sample_rate, simulator.channels, 
                                       "channel_1", mode=mode)
    
    try:
        await asyncio.wait_for(service.run(simulator.stream()), timeout=120)
    except asyncio.TimeoutError:
        pytest.fail(f"V2 {mode} Integration timed out")

    # In V2, chunks are saved to transcript_chunks in common base
    assert len(service.transcript_chunks) > 0, f"V2 {mode} produced no transcript chunks"
    print(f"\nV2 {mode} Test Success: {len(service.transcript_chunks)} chunks captured.")

@pytest.mark.asyncio
@patch("asyncio.sleep", return_value=None)
async def test_legacy_baseline_integration(mock_sleep):
    """Ensures Legacy Baseline (transcribe.py) can process audio."""
    service = LegacyService(TEST_URI, "channel_1", 0.5)
    
    await service._get_audio_properties()
    # Slicing the MP3 directly is risky but 500k should be around 10-20s
    service.audio_data = service.audio_data[:500000]
    
    try:
        await asyncio.wait_for(service.run(), timeout=120)
    except asyncio.TimeoutError:
        pytest.fail("Legacy Integration timed out")

    assert len(service.accumulated_transcript_chunks) > 0, "Legacy produced no chunks"
    print(f"\nLegacy Test Success: {len(service.accumulated_transcript_chunks)} chunks captured.")