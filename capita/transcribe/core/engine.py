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
        self.GAP_THRESHOLD = 0.5        # Silence between words to trigger a turn split
        self.ACTIVE_BLOCKING = True     # Prevent short interjections from appearing before a monologue ends
        
        # State
        self.stability_buffer: List[TranscriptionEvent] = []
        self.active_starts = {} # {speaker_id: start_sec}
        self.current_audio_time = 0.0
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        
        # Callbacks (Sinks)
        self.sinks: List[Callable[[TranscriptionEvent], None]] = []

    def add_sink(self, sink_func: Callable[[TranscriptionEvent], None]):
        """Attaches a output handler (e.g., Terminal, JSON Log) to the engine."""
        self.sinks.append(sink_func)

    def _emit(self, event: TranscriptionEvent):
        """Internal helper to broadcast events to all attached sinks."""
        # Attach a wall-clock timestamp if missing
        if not event.timestamp:
            ts = self.start_time + datetime.timedelta(seconds=event.start_sec)
            event.timestamp = ts.strftime("%H:%M:%S.%f")[:-5]
            
        for sink in self.sinks:
            sink(event)

    def set_audio_time(self, seconds: float):
        """
        Advances the global playhead. 
        This drives the release of buffered events during periods of API silence.
        """
        self.current_audio_time = seconds
        
        # Automatic Heartbeat: Emit a signal every 1 second of audio time to keep Sinks alive
        if int(seconds) > getattr(self, "_last_heartbeat_floor", -1):
            self._emit(TranscriptionEvent(
                speaker_id=1, text="", start_sec=seconds, end_sec=seconds,
                is_final=False, event_type="heartbeat"
            ))
            self._last_heartbeat_floor = int(seconds)
            
        self._flush_stable_events()

    def process_raw_event(self, event: TranscriptionEvent):
        """Main entry point for raw events coming from API providers."""
        # Sync clock if the event is ahead of the broadcaster (safety fallback)
        self.current_audio_time = max(self.current_audio_time, event.start_sec)

        if not event.is_final:
            # Emit interim (draft) results immediately for a 'live' typing effect
            self._emit(event)
            return

        # Buffer finalized results for chronological sorting and splitting
        self.stability_buffer.append(event)
        self._flush_stable_events()

    def _flush_stable_events(self, force=False):
        """Releases buffered events that have passed the stability window."""
        stable, remaining = [], []
        
        for event in self.stability_buffer:
            # Use end_sec for stability to ensure we have all possible 
            # overlapping interjections from other channels before releasing.
            is_stable_time = self.current_audio_time > event.end_sec + self.STABILITY_THRESHOLD
            
            is_blocked = False
            if self.ACTIVE_BLOCKING:
                for speaker_id, start in self.active_starts.items():
                    if speaker_id != event.speaker_id and start is not None:
                        # Someone else started talking BEFORE this event ended.
                        # We block this event to allow the other speaker's interjection to be woven in.
                        if start < event.end_sec - 0.1:
                            # Block unless we've reached a 3s safety timeout past the event end.
                            if self.current_audio_time < event.end_sec + 3.0:
                                is_blocked = True
                                break
            
            if force or (is_stable_time and not is_blocked):
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        if stable:
            # 1. Natural Turn Splitting:
            # Match Gemini's style by breaking large blocks at silence gaps.
            split_batch = []
            for event in stable:
                if event.event_type == "transcript" and event.words:
                    split_batch.extend(self._split_on_gaps(event))
                else:
                    split_batch.append(event)

            # 2. Interleaving Logic:
            # Splice monologues if interjections occurred during them.
            processed_batch = self._interleave_and_split(split_batch)

            # 3. Final chronological sort before emission
            processed_batch.sort(key=lambda x: (x.start_sec, x.end_sec))
            for event in processed_batch:
                self._emit(event)

    def _interleave_and_split(self, events: List[TranscriptionEvent]) -> List[TranscriptionEvent]:
        """Splits monologues into segments if interjections occurred during them."""
        if len(events) < 2:
            return sorted(events, key=lambda x: (x.start_sec, x.end_sec))

        # Ensure we have word-level timestamps for all transcripts
        for ev in events:
            if ev.event_type == "transcript" and not ev.words and ev.text:
                words = ev.text.split()
                if words:
                    duration = ev.end_sec - ev.start_sec
                    step = max(0.01, duration / len(words))
                    ev.words = [{"word": w, "start": ev.start_sec + i * step} for i, w in enumerate(words)]

        # Separate monologues (to be split) from other events (potential interjections)
        monologues = [e for e in events if e.event_type == "transcript" and e.words]
        others = [e for e in events if not (e.event_type == "transcript" and e.words)]
        
        pieces = others[:]
        for mono in monologues:
            # Find all events from OTHER speakers that overlap this monologue
            interjections = [
                e for e in events 
                if e.speaker_id != mono.speaker_id 
                and e.start_sec < mono.end_sec 
                and e.end_sec > mono.start_sec
            ]
            
            if not interjections:
                pieces.append(mono)
                continue
                
            # Collect all unique split points within the monologue's duration
            split_times = set()
            for inter in interjections:
                if mono.start_sec < inter.start_sec < mono.end_sec:
                    split_times.add(inter.start_sec)
                if mono.start_sec < inter.end_sec < mono.end_sec:
                    split_times.add(inter.end_sec)
            
            if not split_times:
                pieces.append(mono)
                continue
                
            # Process monologue segments chronologically
            sorted_splits = sorted(list(split_times))
            current_mono = mono
            for t in sorted_splits:
                # Find word index for split time t
                split_idx = -1
                for idx, w in enumerate(current_mono.words):
                    if w["start"] >= t:
                        split_idx = idx
                        break
                
                if split_idx > 0:
                    prefix, suffix = self._split_event(current_mono, split_idx, t)
                    if prefix.text.strip():
                        pieces.append(prefix)
                    current_mono = suffix
                # If split_idx is 0 or -1, no split is needed at this time t for current_mono
            
            if current_mono.text.strip():
                pieces.append(current_mono)
                
        return sorted(pieces, key=lambda x: (x.start_sec, x.end_sec))

    def _split_event(self, event: TranscriptionEvent, split_idx: int, split_time: float):
        """Helper to split an event at a given word index."""
        prefix_words = event.words[:split_idx]
        suffix_words = event.words[split_idx:]
        
        prefix = TranscriptionEvent(
            speaker_id=event.speaker_id,
            text=" ".join([w["word"] for w in prefix_words]),
            start_sec=event.start_sec,
            end_sec=split_time,
            is_final=True,
            words=prefix_words,
            timestamp=event.timestamp,
            metadata=event.metadata.copy()
        )
        suffix = TranscriptionEvent(
            speaker_id=event.speaker_id,
            text=" ".join([w["word"] for w in suffix_words]),
            start_sec=split_time,
            end_sec=event.end_sec,
            is_final=True,
            words=suffix_words,
            timestamp=event.timestamp,
            metadata=event.metadata.copy()
        )
        return prefix, suffix

    def _split_on_gaps(self, event: TranscriptionEvent) -> List[TranscriptionEvent]:
        """Splits a single API result into multiple turns based on inter-word silence."""
        if not event.words or len(event.words) < 2:
            return [event]

        turns = []
        current_words = [event.words[0]]
        
        for i in range(1, len(event.words)):
            prev_word = event.words[i-1]
            curr_word = event.words[i]
            
            # Detect silence gap
            gap = curr_word["start"] - prev_word.get("end", prev_word["start"] + 0.1) 
            
            if gap > self.GAP_THRESHOLD:
                # Split here
                text = " ".join([w["word"] for w in current_words])
                turns.append(TranscriptionEvent(
                    speaker_id=event.speaker_id,
                    text=text,
                    start_sec=current_words[0]["start"],
                    end_sec=prev_word.get("end", curr_word["start"]),
                    is_final=True,
                    words=current_words,
                    timestamp=event.timestamp
                ))
                current_words = [curr_word]
            else:
                current_words.append(curr_word)
        
        # Add final segment
        if current_words:
            text = " ".join([w["word"] for w in current_words])
            turns.append(TranscriptionEvent(
                speaker_id=event.speaker_id,
                text=text,
                start_sec=current_words[0]["start"],
                end_sec=event.end_sec,
                is_final=True,
                words=current_words,
                timestamp=event.timestamp
            ))
            
        return turns

    def update_active_status(self, speaker_id: int, start_sec: Optional[float]):
        """Used by workers to signal when a speaker is currently talking (VAD)."""
        self.active_starts[speaker_id] = start_sec

    def shutdown(self):
        """Flushes all remaining events before closing."""
        self._flush_stable_events(force=True)
