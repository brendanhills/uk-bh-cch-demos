"""
The 'Brain' of the transcription system.
Handles chronological stabilization, natural turn splitting (gap detection),
and interjection management.
"""

import datetime
import logging
from typing import List, Callable, Optional
from .models import TranscriptionEvent

class TranscriptionEngine:
    """
    Consumer-side engine that reconstructs a globally ordered timeline from
    potentially out-of-order or overlapping API results.
    """
    def __init__(self):
        # Configuration
        self.STABILITY_THRESHOLD = 1.0  # Seconds to hold results for sorting
        self.GAP_THRESHOLD = 1.5        # Silence between words to trigger a turn split
        self.ACTIVE_BLOCKING = True     # Prevent short interjections from appearing before a monologue ends
        
        # State
        self.stability_buffer: List[TranscriptionEvent] = []
        self.active_starts = {} # {speaker_id: start_sec} - current active speech
        self.last_vad_starts = {} # {speaker_id: start_sec} - most recent VAD begin
        self.current_audio_time = 0.0
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Callbacks (Sinks)
        self.sinks: List[Callable[[TranscriptionEvent], None]] = []

    def add_sink(self, sink_func: Callable[[TranscriptionEvent], None]):
        """Attaches a output handler (e.g., Terminal, JSON Log) to the engine."""
        self.sinks.append(sink_func)

    def _emit(self, event: TranscriptionEvent):
        """Internal helper to broadcast events to all attached sinks."""
        if not event.timestamp:
            ts = self.start_time + datetime.timedelta(seconds=event.start_sec)
            event.timestamp = ts.strftime("%H:%M:%S.%f")[:-5]
            
        for sink in self.sinks:
            sink(event)

    def set_audio_time(self, seconds: float):
        """Advances the global playhead and drives the release of buffered events."""
        self.current_audio_time = seconds
        
        # Automatic Heartbeat: keeps UI active during long silences
        if int(seconds) > getattr(self, "_last_heartbeat_floor", -1):
            self._emit(TranscriptionEvent(
                speaker_id=1, text="", start_sec=seconds, end_sec=seconds,
                is_final=False, event_type="heartbeat"
            ))
            self._last_heartbeat_floor = int(seconds)
            
        self._flush_stable_events()

    def process_raw_event(self, event: TranscriptionEvent):
        """Main entry point for raw events from API providers."""
        self.current_audio_time = max(self.current_audio_time, event.start_sec)

        # 1. Handle VAD events (Voice Activity Detection)
        if event.event_type != "transcript":
            if "begin" in event.event_type:
                self.update_active_status(event.speaker_id, event.start_sec)
                # Only pin to the FIRST begin event in a potential burst
                if self.last_vad_starts.get(event.speaker_id) is None:
                    self.last_vad_starts[event.speaker_id] = event.start_sec
            elif "end" in event.event_type:
                self.update_active_status(event.speaker_id, None)
            
            self._emit(event)
            return

        # 2. Handle interims (drafts)
        if not event.is_final:
            # GATING: Only emit interims if the speaker is currently 'active' (VAD Begin received)
            # This filters out 'hallucinations' that occur during background noise.
            if self.active_starts.get(event.speaker_id) is not None:
                self._emit(event)
            return

        # 3. Handle wordless transcripts (VAD Pinning for Chirp-3)
        if not event.words:
            # Use the most recent VAD start for this speaker
            last_start = self.last_vad_starts.get(event.speaker_id)
            if last_start is not None:
                event.start_sec = last_start
                # Clear the cache once consumed to avoid mis-pinning the next segment
                self.last_vad_starts[event.speaker_id] = None

        # 4. Buffer finalized results for stabilization
        self.stability_buffer.append(event)
        self._flush_stable_events()

    def _flush_stable_events(self, force=False):
        """Releases buffered events that have passed the stability window."""
        stable, remaining = [], []
        
        for event in self.stability_buffer:
            is_stable_time = self.current_audio_time >= event.end_sec + self.STABILITY_THRESHOLD
            
            is_blocked = False
            if self.ACTIVE_BLOCKING:
                for speaker_id, start in self.active_starts.items():
                    if speaker_id != event.speaker_id and start is not None:
                        # Block if someone else is currently talking
                        if start < event.end_sec - 0.1:
                            if self.current_audio_time < event.end_sec + 10.0: # 10s safety timeout
                                is_blocked = True
                                break
            
            if force or (is_stable_time and not is_blocked):
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        if stable:
            # 1. Natural Turn Splitting
            split_batch = []
            for event in stable:
                if event.event_type == "transcript":
                    event.estimate_word_timings()
                    split_batch.extend(event.split_on_gaps(self.GAP_THRESHOLD))
                else:
                    split_batch.append(event)

            # 2. Interleaving Logic
            processed_batch = self._interleave_and_split(split_batch)

            # 3. Final Sort
            processed_batch.sort(key=lambda x: (x.start_sec, x.end_sec, -x.speaker_id))
            for event in processed_batch:
                self._emit(event)

    def _interleave_and_split(self, events: List[TranscriptionEvent]) -> List[TranscriptionEvent]:
        """Splits monologues into segments if interjections occurred during them."""
        if len(events) < 2:
            return sorted(events, key=lambda x: (x.start_sec, x.end_sec))

        # Identify 'Monologues' (eligible to be split) and 'Splitters' (all other events)
        monologues = [e for e in events if e.event_type == "transcript" and (e.end_sec - e.start_sec) >= 5.0]
        others = [e for e in events if e not in monologues]
        
        final_pieces = []
        for mono in monologues:
            segments = [mono]
            
            # Collect unique boundaries from OTHER speakers that overlap this monologue
            split_points = set()
            for other in events:
                if other.speaker_id != mono.speaker_id:
                    if mono.start_sec < other.start_sec < mono.end_sec:
                        split_points.add(other.start_sec)
                    if mono.start_sec < other.end_sec < mono.end_sec:
                        split_points.add(other.end_sec)

            # Apply splits chronologically
            for t in sorted(list(split_points)):
                new_segments = []
                for seg in segments:
                    if seg.start_sec < t < seg.end_sec:
                        seg.estimate_word_timings()
                        split_idx = -1
                        for idx, w in enumerate(seg.words):
                            if w["start"] >= t:
                                split_idx = idx
                                break
                        
                        # ALWAYS split into two pieces at time t to preserve interleaving
                        if split_idx == -1:
                            prefix_words, suffix_words = seg.words, []
                        else:
                            prefix_words, suffix_words = seg.words[:split_idx], seg.words[split_idx:]

                        new_segments.append(seg._create_piece(prefix_words, seg.start_sec, t))
                        new_segments.append(seg._create_piece(suffix_words, t, seg.end_sec))
                    else:
                        new_segments.append(seg)
                segments = new_segments
            
            final_pieces.extend(segments)
                
        # Filter out truly empty (textless) pieces
        return others + [p for p in final_pieces if p.text.strip()]

    def update_active_status(self, speaker_id: int, start_sec: Optional[float]):
        """Signals when a speaker is currently talking (VAD)."""
        self.active_starts[speaker_id] = start_sec

    def shutdown(self):
        """Flushes all remaining events before closing."""
        self._flush_stable_events(force=True)
