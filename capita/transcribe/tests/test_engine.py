import pytest
from core.models import TranscriptionEvent
from core.engine import TranscriptionEngine

def test_engine_stabilization():
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 1.0
    engine.ACTIVE_BLOCKING = False
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # 1. Send interim - should be emitted immediately
    interim = TranscriptionEvent(speaker_id=1, text="hello", start_sec=0.5, end_sec=0.5, is_final=False)
    engine.process_raw_event(interim)
    assert len(events) == 1
    assert events[0].text == "hello"
    
    # 2. Send final - should be buffered
    final = TranscriptionEvent(speaker_id=1, text="world", start_sec=0.5, end_sec=1.5, is_final=True)
    engine.process_raw_event(final)
    assert len(events) == 1 # Still buffered
    
    # 3. Advance clock - should release final
    engine.set_audio_time(2.0)
    # Check transcripts only
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == 2 # 1 interim + 1 final
    assert transcripts[1].text == "world"

def test_engine_interleaving():
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 1.0
    engine.ACTIVE_BLOCKING = True
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # Speaker 1 starts talking at 0.5s
    engine.update_active_status(1, 0.5)
    
    # Speaker 2 sends a final result that started later (1.0s)
    s2_final = TranscriptionEvent(speaker_id=2, text="interjection", start_sec=1.0, end_sec=1.5, is_final=True)
    engine.process_raw_event(s2_final)
    
    # Advance clock - Speaker 2 should be BLOCKED because Speaker 1 is still active
    engine.set_audio_time(2.5)
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == 0 
    
    # Speaker 1 finishes
    engine.update_active_status(1, None)
    engine.set_audio_time(2.6)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == 1
    assert transcripts[0].text == "interjection"

def test_monologue_splitting():
    engine = TranscriptionEngine()
    engine.STABILITY_THRESHOLD = 5.0 # High threshold to ensure both are buffered
    engine.ACTIVE_BLOCKING = False
    
    events = []
    engine.add_sink(lambda e: events.append(e))
    
    # A long monologue from Speaker 1
    s1_long = TranscriptionEvent(
        speaker_id=1, 
        text="I am a very long monologue that should be split",
        start_sec=0.0, end_sec=10.0, is_final=True,
        words=[
            {"word": "I", "start": 0.0},
            {"word": "am", "start": 1.0},
            {"word": "a", "start": 2.0},
            {"word": "very", "start": 3.0},
            {"word": "long", "start": 4.0},
            {"word": "monologue", "start": 5.0},
            {"word": "that", "start": 6.0},
            {"word": "should", "start": 7.0},
            {"word": "be", "start": 8.0},
            {"word": "split", "start": 9.0}
        ]
    )
    
    # A short interjection from Speaker 2
    s2_inter = TranscriptionEvent(
        speaker_id=2, text="Indeed", start_sec=4.5, end_sec=5.5, is_final=True
    )
    
    # Set time to 0 before processing
    engine.set_audio_time(0.0)
    engine.process_raw_event(s1_long)
    engine.process_raw_event(s2_inter)
    
    # Both should be in buffer now because current_audio_time (0.0) is not > start + 5.0
    assert len(engine.stability_buffer) == 2
    
    # Advance clock to release both simultaneously
    engine.set_audio_time(12.0)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    
    # It splits into 4 parts:
    # 1. Speaker 1: [0.0 - 4.5] "I am a very long"
    # 2. Speaker 2: [4.5 - 5.5] "Indeed"
    # 3. Speaker 1: [4.5 - 5.5] "monologue"
    # 4. Speaker 1: [5.5 - 10.0] "that should be split"
    assert len(transcripts) == 4
    assert transcripts[0].speaker_id == 1
    assert transcripts[1].speaker_id == 2
    assert transcripts[2].speaker_id == 1
    assert transcripts[3].speaker_id == 1
    
    assert transcripts[0].text == "I am a very long"
    assert transcripts[1].text == "Indeed"
    assert transcripts[2].text == "monologue"
    assert transcripts[3].text == "that should be split"
