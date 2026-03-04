import subprocess
import os
import re
import json
import time

samples = ["0638.mp3", "4065.mp3", "4157.mp3", "4484.mp3", "4507.mp3", "4520.mp3"]
duration = 60

# Core Approaches and Model Comparisons
approaches = [
    ("Two-Channel (Telephony)", "two_channel_transcribe_v2.py", ["--mode", "readability", "--model", "telephony"]),
    ("Parallel (Telephony)", "parallel_transcribe.py", ["--mode", "readability", "--model", "telephony"]),
    ("Parallel (Chirp-3)", "parallel_transcribe.py", ["--mode", "readability", "--model", "chirp_3"])
]

results = []

def get_stats(golden, stream):
    if not os.path.exists(stream): return "N/A"
    cmd = ["uv", "run", "diff_transcripts.py", "-b", golden, "-s", stream]
    res = subprocess.run(cmd, capture_output=True, text=True)
    for line in res.stdout.split("\n"):
        if "Matches:" in line:
            # Strip ANSI
            return re.sub(r'\x1B(?:[@-Z\-_]|\[[0-?]*[ -/]*[@-~])', '', line).strip()
    return "No stats"

print(f"Starting Fidelity Test Suite ({len(samples)} samples x {len(approaches)} approaches)...")

for sample in samples:
    audio_path = f"samples/{sample}"
    golden_path = f"output/{sample}_golden_set.json"
    
    if not os.path.exists(golden_path):
        print(f"Skipping {sample}, no golden set.")
        continue

    for name, script, extra_args in approaches:
        print(f"  >>> Running {sample} | {name}...")
        
        cmd = ["uv", "run", script, audio_path, "--duration", str(duration)] + extra_args
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        # Find output path
        output_path = None
        for line in proc.stdout.split("\n"):
            if ".json" in line and ("Output" in line):
                clean_line = re.sub(r'\x1B(?:[@-Z\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                if ":" in clean_line:
                    output_path = clean_line.split(":", 1)[1].strip()
                    break
        
        if output_path:
            stats = get_stats(golden_path, output_path)
            results.append({
                "sample": sample,
                "approach": name,
                "stats": stats
            })
        else:
            print(f"      FAILED to generate output for {sample} {name}")
        
        time.sleep(1) # Brief pause

# Output Results Table
print("\n" + "="*120)
print(f"{'Sample':<12} | {'Approach':<20} | {'Summary Stats'}")
print("-" * 120)
for r in results:
    print(f"{r['sample']:<12} | {r['approach']:<20} | {r['stats']}")
print("="*120)
