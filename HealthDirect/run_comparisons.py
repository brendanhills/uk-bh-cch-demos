import subprocess
import os
import time

samples = ["0638.mp3", "4065.mp3", "4157.mp3", "4484.mp3", "4507.mp3", "4520.mp3"]
duration = 60

results = []

for sample in samples:
    audio_path = f"samples/{sample}"
    golden_path = f"output/{sample}_golden_set.json"
    
    if not os.path.exists(golden_path):
        print(f"Skipping {sample}, no golden set.")
        continue
        
    for arch in ["mode_a", "mode_b"]:
        print(f"
>>> Running {sample} with {arch}...")
        
        # 1. Run parallel transcription
        cmd = ["uv", "run", "parallel_transcribe.py", audio_path, "--duration", str(duration), "--arch", arch, "--mode", "readability"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        # 2. Extract output path
        output_path = None
        for line in proc.stdout.split("
"):
            if "Output:" in line:
                output_path = line.split("Output:")[1].strip()
                break
        
        if not output_path or not os.path.exists(output_path):
            print(f"Error: No output for {sample} {arch}")
            continue
            
        # 3. Run comparison
        print(f"Comparing {output_path} to golden...")
        comp_cmd = ["uv", "run", "diff_transcripts.py", "-b", golden_path, "-s", output_path]
        comp_proc = subprocess.run(comp_cmd, capture_output=True, text=True)
        
        # 4. Extract summary stats from comparison output
        # Look for lines like "✓ Matches: 10 | ⚠ Text Diffs: 2 ..."
        summary = "No summary found"
        for line in comp_proc.stdout.split("
"):
            if "Matches:" in line:
                # Clean up ANSI codes
                import re
                clean_line = re.sub(r'\x1B(?:[@-Z\-_]|\[[0-?]*[ -/]*[@-~])', '', line)
                summary = clean_line.strip()
                break
        
        results.append({
            "sample": sample,
            "arch": arch,
            "summary": summary,
            "output": output_path
        })
        
        # Brief pause to avoid quota issues
        time.sleep(2)

# Print Final Summary Table
print("
" + "="*80)
print(f"{'Sample':<12} | {'Arch':<8} | {'Summary'}")
print("-" * 80)
for r in results:
    print(f"{r['sample']:<12} | {r['arch']:<8} | {r['summary']}")
print("="*80)
