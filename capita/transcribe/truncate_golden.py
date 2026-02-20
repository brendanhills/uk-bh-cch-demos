import json

with open('output/4484.mp3_golden_set.json', 'r') as f:
    golden = json.load(f)

# Filter for the first 60 seconds
truncated = [turn for turn in golden if turn['start_sec'] < 60]

with open('output/4484.mp3_golden_60s.json', 'w') as f:
    json.dump(truncated, f, indent=2)

print(f"Truncated golden set to {len(truncated)} turns.")
