import pytest
from core.models import TranscriptionEvent

def test_estimate_word_timings_basic():
    """Verifies that words are evenly distributed across the duration."""
    event = TranscriptionEvent(
        speaker_id=1, text="one two three", start_sec=0.0, end_sec=3.0, is_final=True
    )
    
    # Should create 3 words: [0-1], [1-2], [2-3]
    event.estimate_word_timings()
    
    assert len(event.words) == 3
    assert event.words[0]["word"] == "one"
    assert event.words[0]["start"] == 0.0
    assert event.words[0]["end"] == 1.0
    
    assert event.words[1]["word"] == "two"
    assert event.words[1]["start"] == 1.0
    assert event.words[1]["end"] == 2.0
    
    assert event.words[2]["word"] == "three"
    assert event.words[2]["start"] == 2.0
    assert event.words[2]["end"] == 3.0

def test_estimate_word_timings_already_exists():
    """Verifies that existing words are NOT overwritten."""
    existing_words = [{"word": "test", "start": 1.0, "end": 2.0}]
    event = TranscriptionEvent(
        speaker_id=1, text="test", start_sec=0.0, end_sec=5.0, is_final=True,
        words=existing_words
    )
    
    event.estimate_word_timings()
    assert event.words == existing_words

def test_split_on_gaps_no_gaps():
    """Verifies no splitting occurs if gaps are below threshold."""
    event = TranscriptionEvent(
        speaker_id=1, text="hello world", start_sec=0.0, end_sec=2.0, is_final=True,
        words=[
            {"word": "hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.6, "end": 1.0}
        ]
    )
    
    turns = event.split_on_gaps(threshold=0.5)
    assert len(turns) == 1
    assert turns[0].text == "hello world"

def test_split_on_gaps_with_split():
    """Verifies splitting occurs at large gaps."""
    event = TranscriptionEvent(
        speaker_id=1, text="part one part two", start_sec=0.0, end_sec=10.0, is_final=True,
        words=[
            {"word": "part", "start": 0.0, "end": 0.5},
            {"word": "one", "start": 0.5, "end": 1.0},
            # 4s gap
            {"word": "part", "start": 5.0, "end": 5.5},
            {"word": "two", "start": 5.5, "end": 6.0}
        ]
    )
    
    turns = event.split_on_gaps(threshold=1.0)
    assert len(turns) == 2
    assert turns[0].text == "part one"
    assert turns[0].start_sec == 0.0
    assert turns[0].end_sec == 1.0 # End of 'one'
    
    assert turns[1].text == "part two"
    assert turns[1].start_sec == 5.0 # Start of 'part' (second)
    assert turns[1].end_sec == 10.0 # Original end_sec preserved for final piece
