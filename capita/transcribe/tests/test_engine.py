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
    assert len(events) == 3 # 1 interim + 1 heartbeat + 1 final
    assert events[2].text == "world"

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
    print(f"DEBUG: Engine state at 2.5s - Active: {engine.active_starts}, Buffer: {len(engine.stability_buffer)}")
    engine.set_audio_time(2.5)
    # Check only transcript events
    transcripts = [e for e in events if e.event_type == "transcript"]
    print(f"DEBUG: Transcripts after 2.5s: {transcripts}")
    assert len(transcripts) == 0 
    
    # Speaker 1 finishes
    engine.update_active_status(1, None)
    engine.set_audio_time(2.6)
    
    transcripts = [e for e in events if e.event_type == "transcript"]
    assert len(transcripts) == 1
    assert transcripts[0].text == "interjection"
