import asyncio
import json
import os
import logging
import pytest
import tempfile
from datetime import datetime

from unittest.mock import AsyncMock, MagicMock
from google.api_core import exceptions
from google.cloud.speech_v2 import Recognizer

from transcribe import main as transcribe_main, TranscriptionService

# A list of audio samples for testing transcription.
AUDIO_SAMPLES = [
    "gs://uk-bh-experiments-argolis-us/capita/test_test-transcript-connector.wav",
    "gs://uk-bh-experiments-argolis-us/capita/resources_sample-calls.mp3",
    "gs://uk-bh-experiments-argolis-us/capita/speech_medical_conversation_2.wav",
    "gs://uk-bh-experiments-argolis-us/capita/4507.mp3"
]

# A list of buffer timeouts to test.
BUFFER_TIMEOUTS = [0.5, 2.0, 5.0]

# Define buffer configurations to avoid redundant tests.
# The first tuple is for the non-buffered case (timeout is a placeholder).
# The rest are for the buffered cases with different timeouts.
BUFFER_CONFIGS = [(False, 0.0)] + [(True, timeout) for timeout in BUFFER_TIMEOUTS]

@pytest.fixture
def temp_output_file():
    """Pytest fixture to create and clean up a temporary file for output."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as tmpfile:
        output_filename = tmpfile.name
    
    yield output_filename
    
    # Cleanup
    if os.path.exists(output_filename):
        os.remove(output_filename)

@pytest.mark.asyncio
@pytest.mark.parametrize("audio_uri", AUDIO_SAMPLES)
@pytest.mark.parametrize("use_buffered, buffer_timeout", BUFFER_CONFIGS)
async def test_transcription_produces_valid_output(monkeypatch, caplog, temp_output_file, audio_uri, use_buffered, buffer_timeout):
    """
    Tests that the transcription process runs and produces a valid, sorted JSON output.
    This test is parameterized to run on multiple audio files and with both
    buffered and non-buffered transcription handlers.
    """
    # Set the log level for the caplog fixture to capture INFO-level messages
    caplog.set_level(logging.INFO)

    # Construct arguments for the main script
    args = ["transcribe.py", audio_uri]
    if use_buffered:
        args.append('--use-buffered')
        args.extend(['--buffer-timeout', str(buffer_timeout)])

    # Monkeypatch sys.argv to simulate command-line execution
    monkeypatch.setattr("sys.argv", args)
    # Monkeypatch the output filename to use our temporary file
    monkeypatch.setattr("transcribe.OUTPUT_FILENAME", temp_output_file)

    # Run the main async function from the application
    await transcribe_main()

    # Read and validate the output from the temporary file
    with open(temp_output_file, 'r') as f:
        # Handle empty file case
        content = f.read()
        if not content:
            pytest.fail(f"Output file is empty for {audio_uri} with use_buffered={use_buffered}")
        
        print(f"\n--- Output for {audio_uri} (buffered={use_buffered}, timeout={buffer_timeout}) ---")
        print(content)
        print("--------------------------------------------------")
        output_data = json.loads(content)
        
    # 0. Check there is some output
    assert output_data, f"No transcription data produced for {audio_uri} with use_buffered={use_buffered}"

    # 1. Check that the output is a list
    assert isinstance(output_data, list), "Output should be a list of transcript segments."

    # 2. Check the structure of each item in the list
    for item in output_data:
        assert isinstance(item, dict)
        assert "speaker" in item
        assert "text" in item
        assert "timestamp" in item

    # 3. Check that timestamps are chronologically sorted
    timestamps = [datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S") for item in output_data]
    assert timestamps == sorted(timestamps), "Timestamps are not in chronological order."

    # 4. Check that the sorting log message is present
    log_text = caplog.text
    sorted_message_found = "have been sorted by timestamp" in log_text
    not_sorted_message_found = "did not need to be sorted" in log_text
    assert sorted_message_found or not_sorted_message_found, "Sorting log message not found in output."

def test_environment_variables_are_set():
    """Tests if necessary environment variables for the application are set."""
    assert os.getenv("PROJECT_ID"), "PROJECT_ID environment variable is not set."
    assert os.getenv("GCP_RECOGNIZER_ID"), "GCP_RECOGNIZER_ID environment variable is not set."

@pytest.mark.asyncio
async def test_find_or_create_recognizer_finds_existing(monkeypatch):
    """Tests that an existing, active recognizer is found and used."""
    # Arrange
    mock_recognizer = MagicMock(spec=Recognizer)
    mock_recognizer.name = "projects/test-project/locations/us-central1/recognizers/test-recognizer"
    mock_recognizer.state = Recognizer.State.ACTIVE

    mock_speech_client = MagicMock()
    mock_speech_client.get_recognizer = AsyncMock(return_value=mock_recognizer)
    mock_speech_client.create_recognizer = AsyncMock()

    # Patch the SpeechAsyncClient to return our mock
    monkeypatch.setattr("transcribe.cs.SpeechAsyncClient", lambda client_options: mock_speech_client)
    
    # Instantiate the service
    service = TranscriptionService(gcs_uri="gs://dummy/uri", customer_channel="channel_1", buffer_timeout=0.5)

    # Act
    recognizer = await service.find_or_create_recognizer(recognizer_id="test-recognizer")

    # Assert
    mock_speech_client.get_recognizer.assert_called_once()
    mock_speech_client.create_recognizer.assert_not_called()
    assert recognizer.name == mock_recognizer.name

@pytest.mark.asyncio
async def test_find_or_create_recognizer_creates_new_when_not_found(monkeypatch):
    """Tests that a new recognizer is created when none is found."""
    # Arrange
    mock_created_recognizer = MagicMock(spec=Recognizer)
    mock_created_recognizer.name = "projects/test-project/locations/us-central1/recognizers/new-recognizer"
    
    mock_operation = MagicMock()
    mock_operation.result = AsyncMock(return_value=mock_created_recognizer)

    mock_speech_client = MagicMock()
    mock_speech_client.get_recognizer = AsyncMock(side_effect=exceptions.NotFound("Recognizer not found"))
    mock_speech_client.create_recognizer = AsyncMock(return_value=mock_operation)

    monkeypatch.setattr("transcribe.cs.SpeechAsyncClient", lambda client_options: mock_speech_client)
    
    service = TranscriptionService(gcs_uri="gs://dummy/uri", customer_channel="channel_1", buffer_timeout=0.5)

    # Act
    recognizer = await service.find_or_create_recognizer(recognizer_id="new-recognizer")

    # Assert
    mock_speech_client.get_recognizer.assert_called_once()
    mock_speech_client.create_recognizer.assert_called_once()
    assert recognizer.name == mock_created_recognizer.name

@pytest.mark.asyncio
async def test_find_or_create_recognizer_creates_new_when_existing_is_not_active(monkeypatch):
    """Tests that a new recognizer is created if the existing one is not in an ACTIVE state."""
    # Arrange
    mock_inactive_recognizer = MagicMock(spec=Recognizer)
    mock_inactive_recognizer.name = "projects/test-project/locations/us-central1/recognizers/inactive-recognizer"
    mock_inactive_recognizer.state = Recognizer.State.DELETING # A non-active state

    # This setup is identical to the 'not_found' test, as the logic path should be the same.
    mock_created_recognizer = MagicMock(spec=Recognizer)
    mock_created_recognizer.name = "projects/test-project/locations/us-central1/recognizers/inactive-recognizer"
    mock_operation = MagicMock()
    mock_operation.result = AsyncMock(return_value=mock_created_recognizer)
    mock_speech_client = MagicMock()
    mock_speech_client.get_recognizer = AsyncMock(return_value=mock_inactive_recognizer)
    mock_speech_client.create_recognizer = AsyncMock(return_value=mock_operation)

    monkeypatch.setattr("transcribe.cs.SpeechAsyncClient", lambda client_options: mock_speech_client)
    
    service = TranscriptionService(gcs_uri="gs://dummy/uri", customer_channel="channel_1", buffer_timeout=0.5)

    # Act
    recognizer = await service.find_or_create_recognizer(recognizer_id="inactive-recognizer")

    # Assert
    mock_speech_client.get_recognizer.assert_called_once()
    mock_speech_client.create_recognizer.assert_called_once()
    assert recognizer.name == mock_created_recognizer.name