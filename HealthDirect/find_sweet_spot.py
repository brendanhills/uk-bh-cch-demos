import subprocess
import json
import os
import re
import time

def clean_text(text):
    text = str(text).lower()
    return " ".join(re.sub(r'[^a-z0-9]', ' ', text).split())

def check_sequence(stability):
    """Runs the demo and returns True if the sequence is correct."""
    audio_sample = "gs://uk-bh-experiments-argolis-us/HealthDirect/call_samples/0638.mp3"
    cmd = [
        "uv", "run", "two_channel_transcribe_v2.py", 
        audio_sample, 
        "--duration", "25", # 25s is enough to capture the first 3 turns
        "--model", "chirp_3",
        "--stability", f"{stability:.1f}",
        "--gap", "1.5"
    ]
    
    print(f"Testing Stability: {stability:4.1f}s ... ", end="", flush=True)
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print("CRASH")
        return False

    # Extract output path
    output_path = None
    for line in process.stdout.split("\n"):
        if ".json" in line and "Output File" in line:
            output_path = line.split(":", 1)[1].strip()
            break
            
    if not output_path or not os.path.exists(output_path):
        print("NO OUTPUT")
        return False
    
    with open(output_path, "r") as f:
        produced = json.load(f)

    transcripts = [t for t in produced if t["text"].strip()]
    
    s2_idx = -1
    s1_idx = -1
    
    for i, t in enumerate(transcripts):
        text = clean_text(t["text"])
        if t["speaker"] == 2 and "how are you" in text:
            s2_idx = i
        if t["speaker"] == 1 and "fine" in text:
            s1_idx = i
            
    if s2_idx == -1 or s1_idx == -1:
        print("MISSING TURNS")
        return False
    
    if s2_idx < s1_idx:
        print("PASS")
        return True
    else:
        print("FAIL")
        return False

def main():
    low = 0.0
    high = 30.0
    sweet_spot = high
    found_any = False

    print("Searching for the sequencing 'Sweet Spot' using Binary Search...")
    print("-" * 60)

    # Perform 6 iterations for ~0.5s precision
    for i in range(6):
        mid = (low + high) / 2
        if check_sequence(mid):
            sweet_spot = mid
            high = mid
            found_any = True
        else:
            low = mid

    print("-" * 60)
    if found_any:
        print(f"FOUND IT: Minimum Stability Threshold is approximately {sweet_spot:.1f} seconds.")
    else:
        print("FAILURE: Even 30 seconds of buffering did not fix the Chirp-3 sequence.")

if __name__ == "__main__":
    main()
