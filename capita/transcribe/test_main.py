import os
import re
import pytest
from datetime import datetime
import main as transcribe_app

# A list of audio samples for strict testing of timestamps and diarization.
AUDIO_SAMPLES = [
    "gs://uk-bh-experiments-argolis-us/capita/test_test-transcript-connector.wav",
    "gs://uk-bh-experiments-argolis-us/capita/resources_sample-calls.mp3",
    "gs://uk-bh-experiments-argolis-us/capita/speech_medical_conversation_2.wav",
]

@pytest.mark.parametrize("audio_uri", AUDIO_SAMPLES)
def test_strict_timestamp_and_diarization(capsys, monkeypatch, audio_uri):
    """
    Tests that every line of dialogue has a valid, monotonically increasing
    timestamp and a speaker label in the format 'HH:MM:SS Speaker X:'.
    """
    # Use monkeypatch to simulate command-line arguments for main.py
    monkeypatch.setattr("sys.argv", ["main.py", audio_uri])

    # Run the main function from the application
    transcribe_app.main()

    # Capture the standard output
    captured = capsys.readouterr()
    output = captured.out

    # Basic checks for successful transcription flow
    assert "--- Transcription ---" in output
    assert "An error occurred" not in output
    assert "Publisher Model" not in output

    # Isolate the transcription block and filter for dialogue lines
    try:
        transcription_block = output.split("--- Transcription ---")[1]
    except IndexError:
        pytest.fail("Transcription block with '--- Transcription ---' not found.")

    dialogue_lines = [
        line.strip() for line in transcription_block.split('\n') 
        if "Speaker" in line or "Automated System" in line
    ]

    # Ensure there are dialogue lines to test
    assert len(dialogue_lines) > 0, "No dialogue lines with speakers found in the output."

    time_format = "%H:%M:%S"
    last_timestamp = None
    # Regex to match "HH:MM:SS Speaker X:" or "HH:MM:SS Automated System:"
    line_pattern = re.compile(r"^(\d{2}:\d{2}:\d{2}) (Speaker \d+|Automated System):")

    for line in dialogue_lines:
        match = line_pattern.match(line)
        
        # 1. Check if the line has the required 'HH:MM:SS Speaker X:' format
        assert match, f"Line does not match 'HH:MM:SS Speaker X:' format: '{line}'"
        
        # 2. Check if timestamps are monotonically increasing
        timestamp_str = match.group(1)
        try:
            current_timestamp = datetime.strptime(timestamp_str, time_format).time()
        except ValueError:
            pytest.fail(f"Invalid timestamp format in line: '{line}'")

        if last_timestamp:
            assert current_timestamp >= last_timestamp, (
                f"Timestamps are not in chronological order. "
                f"Previous: {last_timestamp}, Current: {current_timestamp} in line: '{line}'"
            )
        
        last_timestamp = current_timestamp

def test_environment_variables_set():
    """Tests if necessary environment variables for the application are set."""
    assert os.getenv("GOOGLE_CLOUD_PROJECT") is not None, "GOOGLE_CLOUD_PROJECT is not set."
    assert os.getenv("LOCATION") is not None, "LOCATION is not set."
    assert os.getenv("GCS_BUCKET_NAME") is not None, "GCS_BUCKET_NAME is not set."
