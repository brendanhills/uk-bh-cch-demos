import pytest
from core.models import TranscriptionEvent
from core.engine import TranscriptionEngine

@pytest.mark.parametrize("stability, end_sec, clock, expected_count", [
    (1.0, 1.5, 2.0, 0), # Not yet stable (1.5 + 1.0 = 2.5)
    (1.0, 1.5, 3.0, 1), # Stable
    (0.0, 1.5, 1.6, 1), # Low latency / Immediate
    (5.0, 1.5, 6.0, 0), # Long buffer
])
def test_engine_stability_ranges(stability, end_sec, clock, expected_count):
    """Tests engine stabilization across various thresholds and timings."""
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = stability
    engine.ACTIVE_BLOCKING = False
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    final = TranscriptionEvent(speaker_id=1, text="test", start_sec=0.5, end_sec=end_sec, is_final=True)
    engine.process_raw_event(final)
    
    engine.set_audio_time(clock)
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == expected_count

@pytest.mark.parametrize("gap, expected_turns", [
    (0.5, 2), # Default gap (0.5s < 1.0s silence) -> split
    (2.0, 1), # Large gap threshold (2.0s > 1.0s silence) -> no split
    (0.1, 2), # Aggressive split
])
def test_engine_gap_ranges(gap, expected_turns):
    """Tests natural turn splitting across various gap thresholds."""
    engine = TranscriptionEngine()
    engine.GAP_THRESHOLD = gap
    engine.STABILITY_THRESHOLD = 0.0
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # Event with a 1.0s silence gap between words
    event = TranscriptionEvent(
        speaker_id=1, text="hello world", start_sec=0.0, end_sec=2.0, is_final=True,
        words=[
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 1.5, "end": 2.0}
        ]
    )
    
    engine.process_raw_event(event)
    engine.set_audio_time(5.0)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == expected_turns

def test_engine_interleaving_blocking_toggle():
    """Verifies ACTIVE_BLOCKING prevents interjections when enabled, and allows them when disabled."""
    # 1. With Blocking (Mode A behavior)
    engine = TranscriptionEngine()
    engine.ACTIVE_BLOCKING = True
    engine.STABILITY_THRESHOLD = 0.0
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    engine.update_active_status(1, 0.5) # Speaker 1 is talking
    s2_final = TranscriptionEvent(speaker_id=2, text="hey", start_sec=1.0, end_sec=1.1, is_final=True)
    engine.process_raw_event(s2_final)
    
    engine.set_audio_time(2.0)
    assert len([e for e in events if e.event_type == "transcript"]) == 0 # Blocked
    
    # 2. Without Blocking (Mode B / Low Latency behavior)
    engine.ACTIVE_BLOCKING = False
    engine.set_audio_time(2.1)
    assert len([e for e in events if e.event_type == "transcript"]) == 1 # Released

def test_monologue_splitting_basic():
    """Verifies that a monologue is split by a single interjection."""
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 0.0
    engine.ACTIVE_BLOCKING = False
    engine.GAP_THRESHOLD = 10.0
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # S1: "one two three" (0-6s)
    mono = TranscriptionEvent(
        speaker_id=1, text="one two three", start_sec=0.0, end_sec=6.0, is_final=True,
        words=[
            {"word": "one", "start": 1.0},
            {"word": "two", "start": 3.0},
            {"word": "three", "start": 5.0},
        ]
    )
    
    # S2: interjection at 4s
    inter = TranscriptionEvent(speaker_id=2, text="A", start_sec=4.0, end_sec=4.5, is_final=True)
    
    engine.process_raw_event(mono)
    engine.process_raw_event(inter)
    engine.set_audio_time(10.0)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    
    # Expected:
    # 1. S1: "one two" [1.0-4.0]
    # 2. S2: "A" [4.0-4.5]
    # 3. S1: "three" [4.0-6.0] (Wait, piece 2 of S1 starts at 4.0 because of split)
    
    assert len(transcripts) == 3
    assert transcripts[0].speaker_id == 1
    assert transcripts[1].speaker_id == 2
    assert transcripts[2].speaker_id == 1
    
    assert transcripts[0].text == "one two"
    assert transcripts[1].text == "A"
    assert transcripts[2].text == "three"

def test_engine_wordless_interleaving():
    """Verifies that interjections can still be woven in even if word timestamps are missing."""
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 0.0
    engine.ACTIVE_BLOCKING = False
    engine.GAP_THRESHOLD = 10.0
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # S1: Monologue WITHOUT word-level timestamps (e.g., from Chirp or simplified provider)
    mono = TranscriptionEvent(
        speaker_id=1, text="monologue content", start_sec=0.0, end_sec=10.0, is_final=True,
        words=[] # Explicitly empty
    )
    
    # S2: Interjection at 5s
    inter = TranscriptionEvent(speaker_id=2, text="interjection", start_sec=5.0, end_sec=6.0, is_final=True)
    
    engine.process_raw_event(mono)
    engine.process_raw_event(inter)
    engine.set_audio_time(15.0)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    
    # Expected: The engine should estimate word positions and split it
    assert len(transcripts) == 3
    assert transcripts[0].speaker_id == 1
    assert transcripts[1].speaker_id == 2
    assert transcripts[2].speaker_id == 1
    
    assert transcripts[0].text == "monologue"
    assert transcripts[1].text == "interjection"
    assert transcripts[2].text == "content"
