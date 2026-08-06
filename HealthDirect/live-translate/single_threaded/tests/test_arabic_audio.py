import os
import wave
import pytest

def test_arabic_audio_exists_and_valid():
    """Verify that the generated Arabic asthma session audio is stereo, 16kHz, and 16-bit PCM."""
    audio_path = "samples/ar_asthma_session.wav"
    assert os.path.exists(audio_path), "Arabic asthma session WAV file does not exist!"
    
    with wave.open(audio_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        
        # Verify stereo
        assert n_channels == 2, f"Expected stereo (2 channels), got {n_channels}"
        # Verify 16-bit PCM (sample width = 2 bytes)
        assert sampwidth == 2, f"Expected 16-bit PCM (sample width = 2), got {sampwidth}"
        # Verify 16kHz sample rate
        assert framerate == 16000, f"Expected 16000Hz framerate, got {framerate}"
        
        # Ensure it has sufficient length (68 seconds * 16000 frames/sec)
        n_frames = wf.getnframes()
        duration = n_frames / framerate
        assert duration >= 65.0, f"Expected duration around 68s, got {duration}s"
