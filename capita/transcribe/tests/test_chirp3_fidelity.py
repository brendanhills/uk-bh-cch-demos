import pytest
import subprocess
import json
import os
import re

def clean_text(text):
    text = str(text).lower()
    return " ".join(re.sub(r'[^a-z0-9]', ' ', text).split())

def test_chirp3_utterance_sequence():
    """
    CRITICAL FIDELITY TEST:
    Verifies that the sequence of the first 3 major utterances is correct for Chirp-3.
    Expectation (from Golden Set):
    1. Speaker 1: 'Very interesting. So how are you?' (~4.2s - 6.8s)
    2. Speaker 2: 'Okay. How are you?' (~7.0s - 8.5s)
    3. Speaker 1: 'I'm fine.' (~8.7s - 11.2s)
    """
    audio_sample = "samples/0638.mp3"
    
    # Run the standard V2 demo with Chirp-3
    cmd = ["uv", "run", "two_channel_transcribe_v2.py", audio_sample, "--duration", "20", "--model", "chirp_3"]
    
    print(f"\nRunning fidelity check: {' '.join(cmd)}")
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        pytest.fail(f"Demo failed: {process.stderr}")

    # Find the JSON output path
    stdout = process.stdout
    output_path = None
    for line in stdout.split("\n"):
        if ".json" in line and "Output File" in line:
            output_path = line.split(":", 1)[1].strip()
            break
            
    assert output_path, "Could not find output file path in stdout."
    
    with open(output_path, "r") as f:
        produced = json.load(f)

    # Filtering for the first few turns with text
    transcripts = [t for t in produced if t["text"].strip()]
    
    # We want to check if Speaker 2's 'How are you' correctly follows Speaker 1's setup 
    # but PRECEDES Speaker 1's 'I'm fine'.
    
    s2_how_are_you_idx = -1
    s1_im_fine_idx = -1
    
    for i, t in enumerate(transcripts):
        text = clean_text(t["text"])
        if t["speaker"] == 2 and "how are you" in text:
            s2_how_are_you_idx = i
        if t["speaker"] == 1 and "fine" in text:
            s1_im_fine_idx = i
            
    assert s2_how_are_you_idx != -1, "Could not find Speaker 2's 'How are you?'"
    assert s1_im_fine_idx != -1, "Could not find Speaker 1's 'I'm fine.'"
    
    # THE CORE ASSERTION
    assert s2_how_are_you_idx < s1_im_fine_idx, (
        f"SEQUENCE ERROR: Speaker 1 ('I'm fine', idx {s1_im_fine_idx}) "
        f"appeared BEFORE Speaker 2 ('How are you?', idx {s2_how_are_you_idx})."
    )
    
    print("\nFidelity Check Passed: Correct sequence maintained.")
