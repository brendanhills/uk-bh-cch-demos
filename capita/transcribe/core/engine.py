import datetime
import logging
from typing import List, Callable, Optional
from .models import TranscriptionEvent

class TranscriptionEngine:
    """
    The 'Brain' of the system. Handles chronological stabilization, 
    monologue splitting, and interjection detection.
    """
    def __init__(self):
        # Configuration
        self.STABILITY_THRESHOLD = 1.0
        self.GAP_THRESHOLD = 0.5
        self.ACTIVE_BLOCKING = True
        
        # State
        self.stability_buffer: List[TranscriptionEvent] = []
        self.active_starts = {} # {speaker_id: start_sec}
        self.current_audio_time = 0.0
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Callbacks (Sinks)
        self.sinks: List[Callable[[TranscriptionEvent], None]] = []

    def add_sink(self, sink_func: Callable[[TranscriptionEvent], None]):
        self.sinks.append(sink_func)

    def _emit(self, event: TranscriptionEvent):
        """Sends an event to all attached sinks."""
        # Attach a wall-clock timestamp if missing
        if not event.timestamp:
            ts = self.start_time + datetime.timedelta(seconds=event.start_sec)
            event.timestamp = ts.strftime("%H:%M:%S.%f")[:-5]
            
        for sink in self.sinks:
            sink(event)

    def set_audio_time(self, seconds: float):
        """Advances the global playhead. This allows the buffer to release events during silence."""
        self.current_audio_time = seconds
        
        # Automatic Heartbeat: Emit a signal every 1 second of audio time
        if int(seconds) > getattr(self, "_last_heartbeat_floor", -1):
            self._emit(TranscriptionEvent(
                speaker_id=1, text="", start_sec=seconds, end_sec=seconds,
                is_final=False, event_type="heartbeat"
            ))
            self._last_heartbeat_floor = int(seconds)
            
        self._flush_stable_events()

    def process_raw_event(self, event: TranscriptionEvent):
        """Main entry point for raw events from API providers."""
        # Update clock if the event is further ahead (safety fallback)
        self.current_audio_time = max(self.current_audio_time, event.start_sec)

        if not event.is_final:
            # Emit interims immediately for 'live' feel
            self._emit(event)
            return

        # Final events go into the stability buffer for re-ordering
        self.stability_buffer.append(event)
        
        # We always attempt a flush, but the logic in _flush_stable_events
        # must correctly block if ACTIVE_BLOCKING is enabled.
        self._flush_stable_events()

    def _flush_stable_events(self, force=False):
        """Releases events that have passed the stability window."""
        stable, remaining = [], []
        
        for event in self.stability_buffer:
            is_stable_time = self.current_audio_time > event.start_sec + self.STABILITY_THRESHOLD
            
            is_blocked = False
            if self.ACTIVE_BLOCKING:
                for speaker_id, start in self.active_starts.items():
                    if speaker_id != event.speaker_id and start is not None:
                        # Someone else started BEFORE this event began
                        if start < event.start_sec - 0.1:
                            # We block unless we've reached a 2s safety timeout from the event's start
                            if self.current_audio_time < event.start_sec + 2.0:
                                is_blocked = True
                                break
            
            # Logic: Release if forced OR (it's stable AND not blocked)
            should_release = force or (is_stable_time and not is_blocked)
            
            if should_release:
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        if stable:
            # INTERLEAVING LOGIC:
            # We must check if any event in 'stable' can be split by another event in 'stable'
            released = self._interleave_and_split(stable)
            for event in released:
                self._emit(event)

    def _interleave_and_split(self, events: List[TranscriptionEvent]) -> List[TranscriptionEvent]:
        """Splits monologues into segments if interjections occurred during them."""
        if len(events) < 2:
            return sorted(events, key=lambda x: x.start_sec)

        # 1. Sort by start time
        events.sort(key=lambda x: x.start_sec)
        
        result = []
        while events:
            current = events.pop(0)
            
            # Check for overlaps with subsequent events from DIFFERENT speakers
            overlap_found = False
            for i, other in enumerate(events):
                if other.speaker_id != current.speaker_id and other.start_sec < current.end_sec:
                    # Potential interjection! 
                    if current.words:
                        # 1. Split at other.start_sec
                        split_idx = -1
                        for idx, w in enumerate(current.words):
                            if w["start"] >= other.start_sec:
                                split_idx = idx
                                break
                        
                        if split_idx > 0:
                            prefix, suffix = self._split_event(current, split_idx, other.start_sec)
                            result.append(prefix)
                            events.insert(i, suffix)
                            overlap_found = True
                            break
                        
                        # 2. If already past start, split at other.end_sec
                        split_idx = -1
                        for idx, w in enumerate(current.words):
                            if w["start"] >= other.end_sec:
                                split_idx = idx
                                break
                        
                        if split_idx > 0:
                            prefix, suffix = self._split_event(current, split_idx, other.end_sec)
                            result.append(other)
                            events.pop(i)
                            events.insert(0, prefix)
                            events.insert(1, suffix)
                            overlap_found = True
                            break
            
            if not overlap_found:
                result.append(current)
                
        # Final sort to ensure stable chronological order
        return sorted(result, key=lambda x: (x.start_sec, x.end_sec))

    def _split_event(self, event: TranscriptionEvent, split_idx: int, split_time: float):
        """Helper to split an event at a given word index."""
        prefix_words = event.words[:split_idx]
        suffix_words = event.words[split_idx:]
        
        prefix_text = " ".join([w["word"] for w in prefix_words])
        suffix_text = " ".join([w["word"] for w in suffix_words])
        
        prefix = TranscriptionEvent(
            speaker_id=event.speaker_id,
            text=prefix_text,
            start_sec=event.start_sec,
            end_sec=split_time,
            is_final=True,
            words=prefix_words,
            timestamp=event.timestamp
        )
        suffix = TranscriptionEvent(
            speaker_id=event.speaker_id,
            text=suffix_text,
            start_sec=split_time,
            end_sec=event.end_sec,
            is_final=True,
            words=suffix_words,
            timestamp=event.timestamp
        )
        return prefix, suffix

    def update_active_status(self, speaker_id: int, start_sec: Optional[float]):
        """Tracks when a speaker is currently talking (for blocking logic)."""
        self.active_starts[speaker_id] = start_sec

    def shutdown(self):
        """Ensure everything is emitted before closing."""
        self._flush_stable_events(force=True)
