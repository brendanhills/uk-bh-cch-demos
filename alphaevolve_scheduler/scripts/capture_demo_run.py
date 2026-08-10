#!/usr/bin/env python3
"""Capture script to snapshot live AlphaEvolve GCP runs into Demo Mode candidate feed fixtures.

Usage:
    python3 scripts/capture_demo_run.py
"""

import sys
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def capture_demo_run():
    live_feed = ROOT / "data" / "candidates_feed.jsonl"
    dest_feed = ROOT / "fixtures" / "mock_candidates_feed.jsonl"

    if not live_feed.exists():
        print(f"Error: {live_feed} does not exist. Run a live optimization first!")
        sys.exit(1)

    lines = [line.strip() for line in live_feed.read_text().split("\n") if line.strip()]
    print(f"Loaded {len(lines)} candidate entries from {live_feed}")

    shutil.copy(live_feed, dest_feed)
    print(f"✓ Successfully captured live candidate feed: {live_feed} -> {dest_feed}")

if __name__ == "__main__":
    capture_demo_run()
