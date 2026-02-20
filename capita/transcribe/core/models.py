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

    def to_dict(self):
        """Converts the event to a flat dictionary for JSON logging and Golden Set comparison."""
        return {
            "start_sec": round(self.start_sec, 3),
            "end_sec": round(self.end_sec, 3),
            "speaker": self.speaker_id,
            "text": self.text.strip(),
            "timestamp": self.timestamp or "",
            "event_type": self.event_type
        }
