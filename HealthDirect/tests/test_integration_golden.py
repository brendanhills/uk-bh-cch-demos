import pytest
import subprocess
import json
import os
import difflib
import string
import re
from pathlib import Path

def clean_text(text):
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

@pytest.mark.order("last")
@pytest.mark.parametrize("script, is_parallel, model", [
    ("two_channel_transcribe_v2.py", False, "telephony"),
    ("two_channel_transcribe_v2.py", False, "chirp_3"),
    ("parallel_transcribe.py", True, "telephony"),
    ("parallel_transcribe.py", True, "chirp_3"),
])
def test_transcription_vs_golden(script, is_parallel, model):

    arch = "parallel" if is_parallel else "two_channel"
    audio_sample = "gs://uk-bh-experiments-argolis-us/HealthDirect/call_samples/0638.mp3"
    golden_path = "output/0638.mp3_golden_set.json"
    
    # 1. Run the script
    cmd = ["uv", "run", script, audio_sample, "--duration", "15", "--model", model]
    
    # Scripts that are not Mono V1 support --mode
    if "mono_transcribe_v1" not in script:
        cmd.extend(["--mode", "readability"])
        
    print(f"\nRunning command: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    stdout_lines = []
    for line in process.stdout:
        print(line, end="") # Stream to console to keep session alive
        stdout_lines.append(line)
    
    process.wait()
    stdout = "".join(stdout_lines)
    
    if process.returncode != 0:
        pytest.fail(f"Script {script} failed with exit code {process.returncode}\n")

    # Extract output path
    output_path = None
    for line in stdout.split("\n"):
        if (".json" in line) and ("Output" in line):
            clean_line = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
            if ":" in clean_line:
                output_path = clean_line.split(":", 1)[1].strip()
                break
            
    assert output_path is not None, f"Could not find output path in stdout:\n{stdout}"
    assert os.path.exists(output_path), f"Output file {output_path} does not exist"
    
    # 2. Load data
    with open(golden_path, "r") as f:
        golden = json.load(f)
    with open(output_path, "r") as f:
        produced = json.load(f)
        
    # 3. Fuzzy match first few turns
    golden_trimmed = [t for t in golden if t["start_sec"] < 13.0]
    
    matches = 0
    for g_turn in golden_trimmed:
        g_clean = clean_text(g_turn["text"])
        if not g_clean: continue
        
        found = False
        for p_turn in produced:
            p_clean = clean_text(p_turn["text"])
            if (g_clean in p_clean or p_clean in g_clean or difflib.SequenceMatcher(None, g_clean, p_clean).ratio() > 0.6) \
               and (p_turn["speaker"] == g_turn["speaker"]):
                found = True
                break
        if found:
            matches += 1
            
    match_ratio = matches / len(golden_trimmed) if golden_trimmed else 0
    # Increase leniency for V1 Diarization
    required_ratio = 0.15 if "mono_v1" in output_path else 0.4
    assert match_ratio >= required_ratio, f"Only {matches}/{len(golden_trimmed)} golden turns matched in {script} (Ratio: {match_ratio:.2f})"

    # 4. Check UI components
    has_s1_ui = False
    has_s2_ui = False
    has_heartbeats = False
    has_vad = False
    
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    for line in stdout.split("\n"):
        clean_line = ansi_escape.sub('', line)
        if "Speaker 1:" in clean_line:
            if len(clean_line) - len(clean_line.lstrip()) < 15:
                has_s1_ui = True
        if "Speaker 2:" in clean_line:
            if len(clean_line) - len(clean_line.lstrip()) >= 25:
                has_s2_ui = True

        # Heartbeat and VAD checks (Refactored UI)
        # Heartbeats are lines containing dots or pluses that are not transcript lines
        if "Speaker" not in clean_line:
            if "." in clean_line:
                has_heartbeats = True
            if "+" in clean_line:
                has_vad = True

    assert has_s1_ui, f"UI for {script} {arch} missing Speaker 1 output or alignment is wrong"
    assert has_s2_ui, f"UI for {script} {arch} missing Speaker 2 output or alignment is wrong"
    assert has_heartbeats, f"UI for {script} {arch} missing heartbeats"
    
    if "mono_transcribe_v1" not in script:
        assert has_vad, f"UI for {script} {arch} missing VAD markers"

    print(f"\nIntegration Test Passed for {script} {arch}: {matches} matches.")
