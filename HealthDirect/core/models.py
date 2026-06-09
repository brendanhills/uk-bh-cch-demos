"""
Shared Data Models for the Transcription Pipeline.
These classes ensure a consistent message schema between Producers (API Providers)
and Consumers (Engine and UI Sinks).
"""

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TranscriptionEvent:
    """
    Standardized event representing a piece of recognized speech or a system marker.
    
    Lifecycle:
    1. PRODUCER (Providers) creates an event from raw API responses.
    2. ENGINE processes the event (handles stability, gap-splitting, sorting).
    3. CONSUMER (Sinks) renders or logs the finalized event.
    """
    speaker_id: int
    text: str
    start_sec: float
    end_sec: float
    is_final: bool
    
    # Event Types:
    # - "transcript": Standard speech result.
    # - "speech_activity_begin": VAD start (start_sec is valid).
    # - "speech_activity_end": VAD end (end_sec is valid).
    # - "heartbeat": System signal used to drive the engine clock during silence.
    event_type: str = "transcript"
    
    # Optional raw word data for surgical operations like gap-splitting.
    # Expected format: [{"word": str, "start": float, "end": float}, ...]
    words: List[dict] = field(default_factory=list)
    
    # Human-readable wall-clock timestamp (e.g., "14:30:05.1").
    timestamp: Optional[str] = None
    
    # Optional metadata for comparison (e.g., {"model": "telephony"})
    metadata: dict = field(default_factory=dict)

    def estimate_word_timings(self):
        """
        If the event lacks word-level timestamps (e.g., from Chirp-3), 
        evenly distributes words across the total duration.
        """
        if self.words or not self.text:
            return
            
        words = self.text.split()
        if not words:
            return
            
        duration = self.end_sec - self.start_sec
        if duration <= 0:
            duration = 0.5 # Minimal fallback
            
        step = duration / len(words)
        self.words = [
            {
                "word": w, 
                "start": round(self.start_sec + i * step, 3), 
                "end": round(self.start_sec + (i + 1) * step, 3)
            } 
            for i, w in enumerate(words)
        ]

    def split_on_gaps(self, threshold: float) -> List["TranscriptionEvent"]:
        """
        Surgically partitions a single result into multiple turns based on inter-word silence.
        Returns a list of new TranscriptionEvent objects.
        """
        if not self.words or len(self.words) < 2:
            return [self]

        turns = []
        current_words = [self.words[0]]
        
        for i in range(1, len(self.words)):
            prev_word = self.words[i-1]
            curr_word = self.words[i]
            
            # Detect silence gap
            gap = curr_word["start"] - prev_word.get("end", prev_word["start"] + 0.1) 
            
            if gap > threshold:
                # Create a new piece for the words collected so far
                turns.append(self._create_piece(current_words, current_words[0]["start"], prev_word.get("end", curr_word["start"])))
                current_words = [curr_word]
            else:
                current_words.append(curr_word)
        
        # Add the final collected words as the last piece
        if current_words:
            # We preserve the original end_sec for the very last piece
            turns.append(self._create_piece(current_words, current_words[0]["start"], self.end_sec))
            
        return turns

    def _create_piece(self, words: List[dict], start: float, end: float) -> "TranscriptionEvent":
        """Helper to spawn a new event piece from a subset of words."""
        return TranscriptionEvent(
            speaker_id=self.speaker_id,
            text=" ".join([w["word"] for w in words]),
            start_sec=start,
            end_sec=end,
            is_final=self.is_final,
            event_type=self.event_type,
            words=words,
            timestamp=self.timestamp,
            metadata=self.metadata.copy()
        )

    def to_dict(self):
        """Converts the event to a flat dictionary for JSON logging and Golden Set comparison."""
        d = {
            "start_sec": round(self.start_sec, 3),
            "end_sec": round(self.end_sec, 3),
            "speaker": self.speaker_id,
            "text": self.text.strip(),
            "timestamp": self.timestamp or "",
            "event_type": self.event_type
        }
        # Include model metadata if present to help with comparison analysis
        if self.metadata and "model" in self.metadata:
            d["model"] = self.metadata["model"]
        return d
