import pytest
import asyncio
from core.models import TranscriptionEvent
from core.engine import TranscriptionEngine
from core.sinks import RealTimeJsonSink
import os

@pytest.mark.asyncio
async def test_unified_refactored_flow():
    """Verifies the unified data flow: wordless event -> estimation -> gap splitting -> emission."""
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 0.0
    engine.GAP_THRESHOLD = 0.5
    
    emitted = []
    engine.add_sink(lambda e: emitted.append(e))
    
    # 1. Simulate a wordless Chirp-3 event
    # Duration 10s, 4 words roughly every 2.5s
    raw_event = TranscriptionEvent(
        speaker_id=1,
        text="one two three four",
        start_sec=0.0,
        end_sec=10.0,
        is_final=True,
        words=[] # Wordless
    )
    
    # 2. Process through engine
    # This should trigger:
    #   - VAD pinning (if active_starts set)
    #   - estimate_word_timings()
    #   - split_on_gaps()
    engine.process_raw_event(raw_event)
    engine.set_audio_time(15.0) # Flush
    
    transcripts = [e for e in emitted if e.event_type == "transcript"]
    
    # Based on GAP_THRESHOLD 0.5 and 10s duration for 4 words:
    # words are [0-2.5], [2.5-5.0], [5.0-7.5], [7.5-10.0]
    # Gaps are all 0.0s because they are contiguous estimates.
    # So it should NOT split into 4 pieces yet (gap threshold is 0.5).
    # This is correct - estimates shouldn't cause arbitrary splits unless gaps exist.
    assert len(transcripts) == 1
    assert len(transcripts[0].words) == 4
    assert transcripts[0].words[0]["start"] == 0.0
    assert transcripts[0].words[-1]["end"] == 10.0

@pytest.mark.asyncio
async def test_to_dict_metadata_inclusion():
    """Verifies that to_dict includes model metadata for analysis."""
    event = TranscriptionEvent(
        speaker_id=1, text="hello", start_sec=1.0, end_sec=2.0, is_final=True,
        metadata={"model": "CHIRP_3"}
    )
    
    data = event.to_dict()
    assert data["model"] == "CHIRP_3"
    assert data["text"] == "hello"
