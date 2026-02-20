"""
Advanced Transcript Evaluator

Categorizes discrepancies between Batch (Ground Truth) and Stream (Live) transcripts:
1. WORD_DIFF: Incorrect transcription (text content differs).
2. ATTRIBUTION_DIFF: Differing speaker attribution for the same text.
3. TIMING_DIFF: Utterance start time differs significantly.
4. OOO_SAME_SPEAKER: Out-of-order sequence for the same speaker.
5. OOO_CROSS_SPEAKER: Out-of-order sequence between different speakers.
"""

import json
import argparse
import difflib

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def analyze_diffs(batch_path, stream_path, timing_threshold=1.0):
    batch = load_json(batch_path)
    stream = load_json(stream_path)

    print(f"\nEvaluating: {batch_path} vs {stream_path}")
    print(f"{'='*80}\n")

    # 1. Alignment Phase: Map Batch indices to Stream indices
    # We use a greedy alignment based on highest similarity within a time window
    alignment = [] # List of (batch_idx, stream_idx)
    used_stream_indices = set()
    
    # Speaker Mapping: Detect if Batch Speaker 1 is actually Stream Speaker 2 etc.
    # We look at the first few aligned turns to build a map.
    speaker_map = {} # {batch_speaker: stream_speaker}

    for b_idx, b_turn in enumerate(batch):
        best_s_idx = -1
        max_sim = 0.0
        
        for s_idx, s_turn in enumerate(stream):
            if s_idx in used_stream_indices:
                continue
            
            # Use a generous window for initial alignment
            if abs(b_turn['start_sec'] - s_turn['start_sec']) < 5.0:
                sim = difflib.SequenceMatcher(None, b_turn['text'].lower(), s_turn['text'].lower()).ratio()
                if sim > max_sim:
                    max_sim = sim
                    best_s_idx = s_idx
        
        if best_s_idx != -1 and max_sim > 0.4: # Lower threshold for discovery
            alignment.append((b_idx, best_s_idx))
            used_stream_indices.add(best_s_idx)
            
            # Auto-discover speaker mapping
            b_spk = b_turn['speaker']
            s_spk = stream[best_s_idx]['speaker']
            if b_spk not in speaker_map:
                speaker_map[b_spk] = s_spk
        else:
            alignment.append((b_idx, None))

    # 2. Categorization Phase
    findings = {
        "WORD_DIFF": [],
        "ATTRIBUTION_DIFF": [],
        "TIMING_DIFF": [],
        "OOO_SAME_SPEAKER": [],
        "OOO_CROSS_SPEAKER": [],
        "MISSING": [],
        "EXTRA": []
    }

    last_s_idx = -1
    last_s_idx_per_speaker = {}

    for b_idx, s_idx in alignment:
        b_turn = batch[b_idx]
        
        if s_idx is None:
            findings["MISSING"].append(b_turn)
            continue
            
        s_turn = stream[s_idx]
        b_speaker = b_turn['speaker']
        mapped_s_speaker = speaker_map.get(b_speaker, b_speaker)

        # --- Check: WORD_DIFF ---
        if b_turn['text'].strip().lower() != s_turn['text'].strip().lower():
            findings["WORD_DIFF"].append({"batch": b_turn, "stream": s_turn})

        # --- Check: ATTRIBUTION_DIFF ---
        # Compare against mapped speaker
        if s_turn['speaker'] != mapped_s_speaker:
            findings["ATTRIBUTION_DIFF"].append({"batch": b_turn, "stream": s_turn})

        # --- Check: TIMING_DIFF ---
        if abs(b_turn['start_sec'] - s_turn['start_sec']) > timing_threshold:
            findings["TIMING_DIFF"].append({"batch": b_turn, "stream": s_turn})

        # --- Check: OOO_CROSS_SPEAKER ---
        if s_idx < last_s_idx:
            findings["OOO_CROSS_SPEAKER"].append({"batch": b_turn, "stream": s_turn})
        last_s_idx = s_idx

        # --- Check: OOO_SAME_SPEAKER ---
        prev_s_idx_for_speaker = last_s_idx_per_speaker.get(b_speaker, -1)
        if s_idx < prev_s_idx_for_speaker:
            findings["OOO_SAME_SPEAKER"].append({"batch": b_turn, "stream": s_turn, "speaker": b_speaker})
        last_s_idx_per_speaker[b_speaker] = s_idx

    # Find 'Extra' in stream
    for s_idx, s_turn in enumerate(stream):
        if s_idx not in used_stream_indices:
            findings["EXTRA"].append(s_turn)

    # 3. Reporting Phase
    def print_finding(title, list_data, color_code):
        if not list_data: return
        print(f"\n\033[{color_code}m[ {title} ({len(list_data)}) ]\033[0m")
        for item in list_data[:10]: # Limit to first 10 for brevity
            if "batch" in item:
                print(f"  @ {item['batch']['start_sec']:.1f}s: B_S{item['batch']['speaker']} -> S_S{item['stream']['speaker']}")
                print(f"    Batch:  {item['batch']['text'][:80]}...")
                print(f"    Stream: {item['stream']['text'][:80]}...")
            else:
                print(f"  @ {item.get('start_sec', 0):.1f}s: S{item.get('speaker', 1)} - {item.get('text', '')[:80]}...")
        if len(list_data) > 10: print(f"  ... and {len(list_data)-10} more.")

    print_finding("ATTRIBUTION ERRORS", findings["ATTRIBUTION_DIFF"], "91")
    print_finding("OUT OF ORDER: CROSS-SPEAKER", findings["OOO_CROSS_SPEAKER"], "95")
    print_finding("OUT OF ORDER: SAME-SPEAKER", findings["OOO_SAME_SPEAKER"], "94")
    print_finding("TIMING DRIFT (>1s)", findings["TIMING_DIFF"], "93")
    print_finding("WORD/TEXT DIFFERENCES", findings["WORD_DIFF"], "90")
    print_finding("MISSING IN STREAM", findings["MISSING"], "31")
    print_finding("EXTRA IN STREAM", findings["EXTRA"], "34")

    print(f"\nSummary Report:")
    print(f"  - Total Aligned Turns: {len(alignment) - len(findings['MISSING'])}")
    print(f"  - Total Potential Errors: {sum(len(v) for v in findings.values())}")
    print(f"  - (See categorized logs above for details)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", default="batch_output.json")
    parser.add_argument("--stream", default="output.json")
    parser.add_argument("--threshold", type=float, default=1.0, help="Timing drift threshold in seconds")
    args = parser.parse_args()
    analyze_diffs(args.batch, args.stream, args.threshold)
