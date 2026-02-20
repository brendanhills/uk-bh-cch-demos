"""
Unified Transcript Evaluator (Chronological View)
Focus: Out of Order, Mistranslation, Incorrect Attribution
"""

import json
import argparse
import difflib
from collections import Counter

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        with open(path, 'r') as f:
            content = f.read().strip()
            if not content: return []
            if not content.endswith(']'):
                last_brace = content.rfind('}')
                if last_brace != -1:
                    content = content[:last_brace+1] + ']'
                else:
                    content = content + ']'
            try:
                return json.loads(content)
            except:
                return []

def clean_text(text):
    """Removes punctuation and extra whitespace for fuzzy comparison."""
    import string
    text = str(text).lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return " ".join(text.split())

def analyze_diffs(batch_path, stream_path, timing_threshold=1.0):
    batch = load_json(batch_path)
    stream = load_json(stream_path)

    if not batch:
        print(f"Error: Could not load batch file {batch_path}")
        return
    if not stream:
        print(f"Error: Could not load stream file {stream_path}")
        return

    # 1. PRE-ALIGNMENT: Build Robust Speaker Map
    speaker_pair_counts = Counter()
    for b_turn in batch:
        b_c = clean_text(b_turn['text'])
        if len(b_c) < 5: continue
        for s_turn in stream:
            if abs(b_turn['start_sec'] - s_turn['start_sec']) < 20.0:
                s_c = clean_text(s_turn['text'])
                if b_c in s_c or s_c in b_c or difflib.SequenceMatcher(None, b_c, s_c).ratio() > 0.6:
                    speaker_pair_counts[(b_turn['speaker'], s_turn['speaker'])] += 1
    
    speaker_map = {}
    for b_spk in {p[0] for p in speaker_pair_counts.keys()}:
        options = {p[1]: count for p, count in speaker_pair_counts.items() if p[0] == b_spk}
        if options:
            speaker_map[b_spk] = max(options, key=options.get)

    print(f"\nEvaluating: {batch_path} vs {stream_path}")
    print(f"{'='*115}")
    print(f"Legend:  ✓ Match | ⚠ Text Diff | ⇄ Attribution | 🚨 Seq Error | ⏳ Timing | ✖ Missing | ✚ Extra")
    print(f"{'='*115}")
    print(f"{'Time':<8} | {'Stat':<4} | {'Speaker':<12} | {'Content (Stream follows Batch if different)':<60}")
    print(f"{'-'*115}")

    # 2. ALIGNMENT PHASE
    # We allow Many-to-One: Multiple golden turns can align to the same stream turn
    alignment = [] # List of (batch_idx, stream_idx or None)
    used_stream_indices = set()

    for b_idx, b_turn in enumerate(batch):
        best_s_idx = -1
        max_sim = 0.0
        b_c = clean_text(b_turn['text'])
        
        for s_idx, s_turn in enumerate(stream):
            if abs(b_turn['start_sec'] - s_turn['start_sec']) < 20.0:
                s_c = clean_text(s_turn['text'])
                ratio = difflib.SequenceMatcher(None, b_c, s_c).ratio()
                if (b_c in s_c or s_c in b_c) and (len(b_c) > 5):
                    ratio = max(ratio, 0.9)
                
                if ratio > max_sim:
                    max_sim = ratio
                    best_s_idx = s_idx
        
        if best_s_idx != -1 and max_sim > 0.5:
            alignment.append((b_idx, best_s_idx))
            used_stream_indices.add(best_s_idx)
        else:
            alignment.append((b_idx, None))

    # Detect REAL Out of Order: Did the stream turn N arrive AFTER stream turn N+1?
    # Since the stream file is written sequentially, we check if start_sec is monotonic
    # WITHIN each speaker channel (inter-speaker overlaps are expected).
    ooo_indices = set()
    last_s_time_per_speaker = {}
    for s_idx, s_turn in enumerate(stream):
        spk = s_turn['speaker']
        if spk in last_s_time_per_speaker:
            if s_turn['start_sec'] < last_s_time_per_speaker[spk] - 0.5:
                ooo_indices.add(s_idx)
        last_s_time_per_speaker[spk] = s_turn['start_sec']

    # 3. UNIFIED TIMELINE
    timeline = []
    for b_idx, s_idx in alignment:
        b_turn = batch[b_idx]
        s_turn = stream[s_idx] if s_idx is not None else None
        timeline.append({
            "time": b_turn['start_sec'],
            "batch": b_turn,
            "stream": s_turn,
            "is_ooo": s_idx in ooo_indices if s_idx is not None else False
        })

    for s_idx, s_turn in enumerate(stream):
        if s_idx not in used_stream_indices:
            timeline.append({
                "time": s_turn['start_sec'],
                "batch": None,
                "stream": s_turn,
                "is_ooo": s_idx in ooo_indices
            })

    timeline.sort(key=lambda x: (x['time'], x['batch']['speaker'] if x['batch'] else 99))
    max_stream_time = stream[-1]['end_sec'] if stream else 0

    # 4. OUTPUT
    C_DIM, C_ERR, C_WARN, C_OK, C_OOO, C_RST = "\033[90m", "\033[91m", "\033[93m", "\033[92m", "\033[95m", "\033[0m"

    for item in timeline:
        b, s = item['batch'], item['stream']
        if b and not s and b['start_sec'] > max_stream_time + 5.0: continue

        time_str = f"{item['time']:05.1f}s"
        stat, spk_str, content_str = " ✓ ", "", ""
        
        if b and s:
            b_spk, s_spk = b['speaker'], s['speaker']
            mapped_s_spk = speaker_map.get(b_spk, b_spk)
            b_clean, s_clean = clean_text(b['text']), clean_text(s['text'])
            similarity = difflib.SequenceMatcher(None, b_clean, s_clean).ratio()
            
            text_diff = similarity < 0.8 and not (b_clean in s_clean or s_clean in b_clean)
            spk_diff = s_spk != mapped_s_spk
            time_diff = abs(b['start_sec'] - s['start_sec']) > timing_threshold
            is_ooo = item['is_ooo']
            
            spk_str = f"S{b_spk}"
            if spk_diff: spk_str = f"S{b_spk} {C_ERR}➔{C_RST} S{s_spk}"
            
            if text_diff or spk_diff or time_diff or is_ooo:
                if is_ooo: stat = f"{C_OOO} 🚨 {C_RST}"
                elif spk_diff: stat = f"{C_ERR} ⇄ {C_RST}"
                elif text_diff: stat = f"{C_WARN} ⚠ {C_RST}"
                elif time_diff: stat = f"{C_WARN} ⏳ {C_RST}"
                
                drift = s['start_sec'] - b['start_sec']
                drift_info = f"{C_WARN}[{drift:+.1f}s]{C_RST} " if abs(drift) > timing_threshold else ""
                content_str = f"{drift_info}{C_DIM}B: {b['text']}{C_RST}\n{' '*13} |      | {' '*12} | {C_OK}S: {s['text']}{C_RST}"
            else:
                content_str = f"{b['text']}"
        elif b:
            stat, spk_str, content_str = f"{C_ERR} ✖ {C_RST}", f"S{b['speaker']}", f"{C_DIM}{b['text']}{C_RST}"
        elif s:
            stat, spk_str, content_str = f"{C_OK} ✚ {C_RST}", f"S{s['speaker']}", f"{C_OK}{s['text']}{C_RST}"

        print(f"{time_str} | {stat} | {spk_str:<12} | {content_str}")

    # 5. SUMMARY
    print(f"{'='*115}")
    stats = Counter()
    for item in timeline:
        b, s = item['batch'], item['stream']
        if b and s:
            b_clean, s_clean = clean_text(b['text']), clean_text(s['text'])
            similarity = difflib.SequenceMatcher(None, b_clean, s_clean).ratio()
            spk_diff = s['speaker'] != speaker_map.get(b['speaker'], b['speaker'])
            time_diff = abs(b['start_sec'] - s['start_sec']) > timing_threshold
            if item['is_ooo']: stats["ooo"] += 1
            elif spk_diff: stats["spk"] += 1
            elif similarity < 0.8 and not (b_clean in s_clean or s_clean in b_clean): stats["text"] += 1
            elif time_diff: stats["time"] += 1
            else: stats["match"] += 1
        elif b and b['start_sec'] <= max_stream_time: stats["miss"] += 1
        elif s: stats["extra"] += 1

    print(f" Summary Stats:")
    print(f"  {C_OK}✓ Matches: {stats['match']}{C_RST} | {C_WARN}⚠ Text Diffs: {stats['text']}{C_RST} | {C_ERR}⇄ Attribution: {stats['spk']}{C_RST}")
    print(f"  {C_OOO}🚨 Seq Errors: {stats['ooo']}{C_RST} | {C_WARN}⏳ Timing Drifts: {stats['time']}{C_RST} | {C_ERR}✖ Missing: {stats['miss']}{C_RST} | {C_OK}✚ Extra: {stats['extra']}{C_RST}")
    mapping_str = " | ".join([f"B_S{k}➔S_S{v}" for k,v in speaker_map.items()])
    print(f" Speaker Mapping: {mapping_str}")
    print(f"{'='*115}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--batch", default="batch_output.json")
    parser.add_argument("-s", "--stream", default="output.json")
    parser.add_argument("-t", "--threshold", type=float, default=1.0)
    args = parser.parse_args()
    analyze_diffs(args.batch, args.stream, args.threshold)
