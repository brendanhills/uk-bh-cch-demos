import pytest
import subprocess
import json
import os
import difflib
import string
from pathlib import Path

def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

def run_script(script_name, audio_path, duration=15):
    """Runs a transcription script and returns (stdout, output_json_path)."""
    cmd = ["uv", "run", script_name, audio_path, "--duration", str(duration)]
    
    # Mono V1 doesn't support --mode
    if "mono_transcribe_v1" not in script_name:
        cmd.extend(["--mode", "readability"])
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Extract output path from stdout
    output_path = None
    for line in result.stdout.split("\n"):
        if "Output File:" in line:
            output_path = line.split("Output File:")[1].strip()
            break
            
    return result.stdout, output_path

@pytest.mark.parametrize("script", ["two_channel_transcribe_v2.py", "parallel_transcribe.py", "mono_transcribe_v1.py"])
def test_transcription_vs_golden(script):
    audio_sample = "samples/0638.mp3"
    golden_path = "output/0638.mp3_golden_set.json"
    
    # 1. Run the script
    stdout, output_path = run_script(script, audio_sample, duration=15)
    
    assert output_path is not None, f"Script {script} failed to produce output path in stdout"
    assert os.path.exists(output_path), f"Output file {output_path} was not created"
    
    # 2. Load data
    with open(golden_path, "r") as f:
        golden = json.load(f)
    with open(output_path, "r") as f:
        produced = json.load(f)
        
    # 3. Fuzzy match first few turns (within first 15 seconds)
    golden_trimmed = [t for t in golden if t["start_sec"] < 13.0] # Allow buffer for 15s run
    
    # We expect at least some matches
    matches = 0
    for g_turn in golden_trimmed:
        g_clean = clean_text(g_turn["text"])
        if not g_clean: continue
        
        found = False
        for p_turn in produced:
            p_clean = clean_text(p_turn["text"])
            # Match if text is similar and speaker matches
            if (g_clean in p_clean or p_clean in g_clean or difflib.SequenceMatcher(None, g_clean, p_clean).ratio() > 0.6) \
               and (p_turn["speaker"] == g_turn["speaker"]):
                found = True
                break
        if found:
            matches += 1
            
    # Success if at least 40% of golden turns in first 13s are found
    # (Mono V1 diarization is notoriously poor, so we are slightly more lenient)
    match_ratio = matches / len(golden_trimmed) if golden_trimmed else 0
    required_ratio = 0.25 if "mono_v1" in output_path else 0.4
    assert match_ratio >= required_ratio, f"Only {matches}/{len(golden_trimmed)} golden turns matched in {script} (Ratio: {match_ratio:.2f})"

    # 4. Check UI (Terminal output) for speaker columns, heartbeats, and markers
    # Speaker 1 should be left-aligned
    # Speaker 2 should be indented
    
    has_s1_ui = False
    has_s2_ui = False
    has_heartbeats = False
    has_vad = False
    
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    for line in stdout.split("\n"):
        clean_line = ansi_escape.sub('', line)
        if "Speaker 1:" in clean_line:
            if len(clean_line) - len(clean_line.lstrip()) < 10:
                has_s1_ui = True
        if "Speaker 2:" in clean_line:
            if len(clean_line) - len(clean_line.lstrip()) >= 30:
                has_s2_ui = True
        if "." in clean_line and len(clean_line.strip()) < 5:
            has_heartbeats = True
        if "<TALKING" in clean_line or "<SILENT" in clean_line:
            has_vad = True
                
    assert has_s1_ui, f"UI for {script} missing Speaker 1 output or alignment is wrong"
    assert has_s2_ui, f"UI for {script} missing Speaker 2 output or alignment is wrong"
    assert has_heartbeats, f"UI for {script} missing heartbeat indicators (.)"
    
    # Mono V1 doesn't produce VAD markers
    if "mono_transcribe_v1" not in script:
        assert has_vad, f"UI for {script} missing VAD markers (<TALKING/@SILENT>)"

    print(f"\nIntegration Test Passed for {script}: {matches} matches, UI components verified.")
