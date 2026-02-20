from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class TranscriptionEvent:
    """Standardized event for the entire transcription pipeline."""
    speaker_id: int
    text: str
    start_sec: float
    end_sec: float
    is_final: bool
    # For non-transcript events like VAD start/end
    event_type: str = "transcript" # "transcript", "vad_start", "vad_end", "heartbeat"
    # Optional raw word data for precision
    words: List[dict] = field(default_factory=list)
    # Formatted timestamp for display/logging
    timestamp: Optional[str] = None

    def to_dict(self):
        """Converts the event to a dictionary matching the 'golden' format."""
        return {
            "start_sec": round(self.start_sec, 3),
            "end_sec": round(self.end_sec, 3),
            "speaker": self.speaker_id,
            "text": self.text.strip(),
            "timestamp": self.timestamp or ""
        }
