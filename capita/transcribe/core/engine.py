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
            
            # Diagnostic log
            if event.event_type == "transcript":
                logging.debug(f"Checking {event.text[:10]} @ {event.start_sec:.1f}s - Clock: {self.current_audio_time:.1f}s, Active: {self.active_starts}, Blocked: {is_blocked}")

            if should_release:
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        if stable:
            # Sort released batch chronologically
            stable.sort(key=lambda x: x.start_sec)
            for event in stable:
                self._emit(event)

    def update_active_status(self, speaker_id: int, start_sec: Optional[float]):
        """Tracks when a speaker is currently talking (for blocking logic)."""
        self.active_starts[speaker_id] = start_sec

    def shutdown(self):
        """Ensure everything is emitted before closing."""
        self._flush_stable_events(force=True)
