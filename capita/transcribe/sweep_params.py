import subprocess
import json
import os
import re

def clean_text(text):
    text = str(text).lower()
    return " ".join(re.sub(r'[^a-z0-9]', ' ', text).split())

def run_test(stability, gap):
    audio_sample = "samples/0638.mp3"
    cmd = [
        "uv", "run", "two_channel_transcribe_v2.py", 
        audio_sample, 
        "--duration", "20", 
        "--model", "chirp_3",
        "--stability", str(stability),
        "--gap", str(gap)
    ]
    
    print(f"Testing: S={stability}s, G={gap}s ... ", end="", flush=True)
    process = subprocess.run(cmd, capture_output=True, text=True)
    
    if process.returncode != 0:
        print(f"FAIL (Crash: {process.stderr[:50]}...)")
        return False, "Crash"

    stdout = process.stdout
    output_path = None
    for line in stdout.split("\n"):
        if ".json" in line and "Output File" in line:
            output_path = line.split(":", 1)[1].strip()
            break
            
    if not output_path:
        print("FAIL (No Output)")
        return False, "No Output"
    
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
        print("FAIL (Missing Turns)")
        return False, "Missing Turns"
    
    if s2_how_are_you_idx < s1_im_fine_idx:
        print("PASS")
        return True, "Success"
    else:
        print("FAIL (Sequence Error)")
        return False, "Sequence Error"

def main():
    stabilities = [1.0, 3.0, 5.0, 7.0, 10.0]
    gaps = [0.5, 1.5, 2.5]
    
    results = []
    for s in stabilities:
        for g in gaps:
            success, msg = run_test(s, g)
            results.append({
                "stability": s,
                "gap": g,
                "success": success,
                "message": msg
            })
            
    print("\n--- Summary ---")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"S={r['stability']}s, G={r['gap']}s: {status} {r['message']}")

if __name__ == "__main__":
    main()
