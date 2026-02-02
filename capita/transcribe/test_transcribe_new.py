import asyncio
import json
import os
import datetime
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from google.cloud import speech_v2 as cs
from dotenv import load_dotenv

from transcribe import (
    JitterBuffer, 
    TranscriptFormatter, 
    TranscriptionConfig, 
    RealTimeTranscriber,
    AudioStreamSimulator
)

# --- JitterBuffer Tests ---

def test_jitter_buffer_sorting():
    buffer = JitterBuffer(timeout=1.0)
    
    # Add items out of order
    t1 = datetime.datetime(2023, 1, 1, 12, 0, 1)
    t2 = datetime.datetime(2023, 1, 1, 12, 0, 2)
    t3 = datetime.datetime(2023, 1, 1, 12, 0, 3)

    chunk1 = {"text": "one", "timestamp_dt": t1}
    chunk2 = {"text": "two", "timestamp_dt": t2}
    chunk3 = {"text": "three", "timestamp_dt": t3}

    buffer.add(chunk3)
    buffer.add(chunk1)
    buffer.add(chunk2)

    assert buffer.buffer == [chunk1, chunk2, chunk3]

def test_jitter_buffer_stability_window():
    buffer = JitterBuffer(timeout=2.0) # 2 second window
    
    start_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
    
    # Add a chunk at T+1s
    c1 = {"text": "c1", "timestamp_dt": start_time + datetime.timedelta(seconds=1)}
    buffer.add(c1)
    
    # Max seen is T+1. Stable cutoff is T+1 - 2 = T-1.
    # c1 is at T+1, so it is NOT stable yet.
    assert buffer.get_stable_chunks() == []

    # Add a chunk at T+4s
    c2 = {"text": "c2", "timestamp_dt": start_time + datetime.timedelta(seconds=4)}
    buffer.add(c2)

    # Max seen is T+4. Stable cutoff is T+4 - 2 = T+2.
    # c1 (T+1) <= T+2, so it SHOULD be stable.
    # c2 (T+4) > T+2, so it is NOT stable.
    
    stable = buffer.get_stable_chunks()
    assert len(stable) == 1
    assert stable[0]["text"] == "c1"
    assert "timestamp_dt" not in stable[0] # Should be cleaned up

    # Flush remaining
    remaining = buffer.flush()
    assert len(remaining) == 1
    assert remaining[0]["text"] == "c2"


# --- TranscriptFormatter Tests ---

def test_transcript_formatter_speaker_attribution():
    config = TranscriptionConfig(
        project_id="p", location="l", recognizer_id="r", model="m", 
        language_code="en", customer_channel="channel_1", buffer_timeout=0.5
    )
    start_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
    formatter = TranscriptFormatter(config, start_time)

    # Result on channel 1 (Customer)
    res1 = MagicMock(spec=cs.SpeechRecognitionResult)
    res1.channel_tag = 1
    res1.alternatives = [MagicMock(transcript="hello", words=[MagicMock(end_offset=datetime.timedelta(seconds=1))])]
    res1.result_end_offset = datetime.timedelta(seconds=1)

    formatted1 = formatter.format_result(res1)
    assert formatted1["speaker"] == "customer"
    assert formatted1["text"] == "hello"

    # Result on channel 2 (Agent)
    res2 = MagicMock(spec=cs.SpeechRecognitionResult)
    res2.channel_tag = 2
    res2.alternatives = [MagicMock(transcript="hi", words=[MagicMock(end_offset=datetime.timedelta(seconds=2))])]
    res2.result_end_offset = datetime.timedelta(seconds=2)

    formatted2 = formatter.format_result(res2)
    assert formatted2["speaker"] == "agent"


# --- End-to-End Mocked Test ---

@pytest.mark.asyncio
async def test_real_time_transcriber_flow(tmp_path):
    # Setup
    output_file = tmp_path / "output.json"
    config = TranscriptionConfig(
        project_id="test-proj", 
        location="us-test", 
        recognizer_id="rec-1", 
        model="telephony", 
        language_code="en-US", 
        customer_channel="channel_1", 
        buffer_timeout=0.1,
        output_filename=str(output_file)
    )

    # Mock Audio Streamer
    mock_streamer = MagicMock(spec=AudioStreamSimulator)
    mock_streamer.sample_rate = 16000
    mock_streamer.channels = 1
    mock_streamer.stream = MagicMock()
    
    # Mock GCP Speech Client
    with patch("transcribe.cs.SpeechAsyncClient") as MockClient:
        mock_client_instance = MockClient.return_value
        
        # Mock get_recognizer to return an existing one
        mock_recognizer = MagicMock()
        mock_recognizer.name = "projects/test-proj/locations/us-test/recognizers/rec-1"
        mock_client_instance.get_recognizer = AsyncMock(return_value=mock_recognizer)

        # Mock streaming_recognize response
        # We simulate a stream of responses
        async def response_generator():
            # Response 1: Final result
            res1 = MagicMock()
            res1.is_final = True
            res1.channel_tag = 1
            alt1 = MagicMock()
            alt1.transcript = "Hello world"
            alt1.words = [MagicMock(end_offset=datetime.timedelta(seconds=1))]
            res1.alternatives = [alt1]
            res1.result_end_offset = datetime.timedelta(seconds=1)
            
            mock_resp1 = MagicMock()
            mock_resp1.results = [res1]
            yield mock_resp1
            
            # Response 2: Final result later
            res2 = MagicMock()
            res2.is_final = True
            res2.channel_tag = 2
            alt2 = MagicMock()
            alt2.transcript = "Hi there"
            alt2.words = [MagicMock(end_offset=datetime.timedelta(seconds=2))]
            res2.alternatives = [alt2]
            res2.result_end_offset = datetime.timedelta(seconds=2)
            
            mock_resp2 = MagicMock()
            mock_resp2.results = [res2]
            yield mock_resp2

        # Configure the mock to be an AsyncMock that returns the generator when awaited
        mock_client_instance.streaming_recognize = AsyncMock(return_value=response_generator())

        # Run Transcriber
        transcriber = RealTimeTranscriber(config)
        
        # We need to mock the internal request generator call because it takes args now
        # But wait, we can just let it run, the mock client will consume whatever generator is passed.
        # We just need to pass a dummy audio stream.
        async def dummy_audio():
            yield b'\x00' * 10
        
        await transcriber.transcribe(dummy_audio(), 16000, 1)

        # Assertions
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        
        assert len(data) == 2
# --- Integration Tests with Real Samples ---

AUDIO_SAMPLES = [
    "gs://uk-bh-experiments-argolis-us/capita/test_test-transcript-connector.wav",
    "gs://uk-bh-experiments-argolis-us/capita/4507.mp3",
    "gs://uk-bh-experiments-argolis-us/capita/4520.mp3"
]

@pytest.mark.asyncio
@pytest.mark.parametrize("audio_uri", AUDIO_SAMPLES)
async def test_integration_with_real_samples(audio_uri, tmp_path):
    output_file = tmp_path / "integration_output.json"
    
    # Load env for real project IDs
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    
    if not project_id or not recognizer_id:
        pytest.skip("PROJECT_ID or GCP_RECOGNIZER_ID not set in environment")

    config = TranscriptionConfig(
        project_id=project_id,
        location="us-central1",
        recognizer_id=recognizer_id,
        model="telephony",
        language_code="en-US",
        customer_channel="channel_1",
        buffer_timeout=1.0,
        output_filename=str(output_file)
    )

    simulator = AudioStreamSimulator(audio_uri)
    await simulator.get_audio_data()
    
    transcriber = RealTimeTranscriber(config)
    await transcriber.transcribe(
        audio_stream=simulator.stream(),
        sample_rate=simulator.sample_rate,
        channels=simulator.channels
    )

    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    if data:
        assert "speaker" in data[0]
        assert "text" in data[0]
