import subprocess
import json
import os
import re
import time

def clean_text(text):
    text = str(text).lower()
    return " ".join(re.sub(r'[^a-z0-9]', ' ', text).split())

def run_test(mode, stability=5.0):
    audio_sample = "gs://uk-bh-experiments-argolis-us/HealthDirect/call_samples/0638.mp3"
    cmd = [
        "uv", "run", "two_channel_transcribe_v2.py", 
        audio_sample, 
        "--duration", "20", 
        "--model", "chirp_3",
        "--mode", mode,
        "--stability", str(stability)
    ]
    
    start_wall = time.time()
    process = subprocess.run(cmd, capture_output=True, text=True)
    end_wall = time.time()
    
    if process.returncode != 0:
        return None, "Crash"

    stdout = process.stdout
    output_path = None
    for line in stdout.split("\n"):
        if ".json" in line and "Output File" in line:
            output_path = line.split(":", 1)[1].strip()
            break
            
    if not output_path:
        return None, "No Output"
    
    with open(output_path, "r") as f:
        produced = json.load(f)

    transcripts = [t for t in produced if t["text"].strip()]
    
    s2_how_are_you_idx = -1
    s1_im_fine_idx = -1
    
    for i, t in enumerate(transcripts):
        text = clean_text(t["text"])
        if t["speaker"] == 2 and "how are you" in text:
            s2_how_are_you_idx = i
        if t["speaker"] == 1 and "fine" in text:
            s1_im_fine_idx = i
            
    if s2_how_are_you_idx == -1 or s1_im_fine_idx == -1:
        return None, "Missing Turns"
    
    sequence_ok = s2_how_are_you_idx < s1_im_fine_idx
    return sequence_ok, f"Wall Time: {end_wall - start_wall:.1f}s"

def main():
    test_cases = [
        ("readability", 7.0),
        ("readability", 15.0),
    ]
    
    print(f"{'Config':<22} | {'Sequence':<10} | {'Perf Metrics'}")
    print("-" * 50)
    
    for mode, s in test_cases:
        ok, msg = run_test(mode, s)
        status = "✅ PASS" if ok else "❌ FAIL"
        if ok is None: status = "⚠️ " + msg
        print(f"{mode + (f' (S={s}s)' if s else ''):<22} | {status:<10} | {msg}")

if __name__ == "__main__":
    main()
