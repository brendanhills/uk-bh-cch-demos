#!/usr/bin/env python3
"""
Pacing and Buffer Clearance Evaluation Utility.
This utility runs a manual side-by-side comparison of different chunk sizes,
pacing setups, and queue clearances using the consolidated Live Interpreter.
"""

import sys
import os
import argparse
import subprocess
import json

# Ensure parent is in load path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(BASE_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

CONFIG_PATH = os.path.join(parent_dir, "demo", "interpreter_config.json")

def print_banner():
    print("=" * 80)
    print(f"║ {'PACING AND CHUNK SIZE IMPACT EVALUATION CONSOLE':^76} ║")
    print("=" * 80)

def load_active_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"❌ Error: Central config not found at {CONFIG_PATH}")
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

def run_evaluation(profile: str, chunk_ms: int, pacing: str, no_glossary: bool):
    print(f"\n🚀 Running profile: {profile.upper()} ({chunk_ms}ms chunks, pacing: {pacing})")
    
    # Save the custom settings temporarily to config for background runners
    orig_config = load_active_config()
    if orig_config:
        temp_config = orig_config.copy()
        temp_config["chunk_ms"] = chunk_ms
        temp_config["pacing_mode"] = pacing
        save_config(temp_config)

    # Command list
    cmd = [
        "uv", "run", "demo/web_server.py", "--cli",
        "--chunk-ms", str(chunk_ms),
        "--pacing", pacing,
        "--stats"
    ]
    if no_glossary:
        cmd.append("--no-glossary")
        
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Evaluation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error running evaluation: {e}")
    finally:
        # Restore original config
        if orig_config:
            save_config(orig_config)

def main():
    parser = argparse.ArgumentParser(description="Pacing and Buffer Clearance Evaluation Utility")
    parser.add_argument(
        "--profile", "-p",
        choices=["legacy", "optimized", "custom"],
        default="optimized",
        help="The settings profile to evaluate: legacy (100ms, simple), optimized (40ms, paced), custom"
    )
    parser.add_argument(
        "--chunk-ms", "-c",
        type=int,
        default=40,
        help="Chunk duration override for 'custom' profile (e.g. 40, 100)"
    )
    parser.add_argument(
        "--pacing-mode",
        choices=["simple", "paced"],
        default="paced",
        help="Pacing mode override for 'custom' profile"
    )
    parser.add_argument(
        "--no-glossary",
        action="store_true",
        help="Bypass translation glossary injection"
    )
    parser.add_argument(
        "--restore-stable",
        action="store_true",
        help="Quickly revert and restore the original stable pacing/chunk defaults"
    )

    args = parser.parse_args()

    print_banner()

    if args.restore_stable:
        config = load_active_config()
        if config:
            config["chunk_ms"] = 100
            config["pacing_mode"] = "simple"
            save_config(config)
            print("✅ Successfully rolled back and restored original stable configuration (100ms chunk, simple pacing).")
        else:
            print("❌ Failed to load active configuration to restore.")
        return

    # Determine profile params
    if args.profile == "legacy":
        chunk_ms = 100
        pacing = "simple"
    elif args.profile == "optimized":
        chunk_ms = 40
        pacing = "paced"
    else:
        chunk_ms = args.chunk_ms
        pacing = args.pacing_mode

    print(f"📝 Evaluation Plan:")
    print(f"   - Target Chunk Duration: {chunk_ms}ms")
    print(f"   - Selected Pacing Mode : {pacing}")
    print(f"   - Glossary Active      : {not args.no_glossary}")
    print("=" * 80)
    
    run_evaluation(args.profile, chunk_ms, pacing, args.no_glossary)

if __name__ == "__main__":
    main()
