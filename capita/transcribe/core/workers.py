"""
Worker classes for independent transcription channels.
Supports both Raw (unbuffered) and Stabilized (local buffering) modes.
"""

import asyncio
import logging
from typing import Optional, List
from .models import TranscriptionEvent
from .providers import V2Provider

class RawChannelWorker:
    """
    Feeds a centralized engine with raw, immediate results.
    Used in 'Mode A' (Consumer-Side Stabilization).
    """
    def __init__(self, provider: V2Provider, channel_id: int):
        self.provider = provider
        self.channel_id = channel_id

    async def run(self, audio_gen, output_queue: asyncio.Queue, chunk_duration_sec: float):
        """Streams audio to provider and pushes all events to output_queue."""
        async for event in self.provider.stream(audio_gen, channel_id=self.channel_id, chunk_duration_sec=chunk_duration_sec):
            await output_queue.put(event)
        await output_queue.put(None)

class StabilizedChannelWorker:
    """
    Implements local stability buffering and gap-splitting.
    Only pushes 'stable' or 'final' segments to the centralized engine.
    Used in 'Mode B' (Producer-Side Stabilization).
    """
    def __init__(self, provider: V2Provider, channel_id: int, stability_threshold: float = 1.0, gap_threshold: float = 0.5):
        self.provider = provider
        self.channel_id = channel_id
        self.STABILITY_THRESHOLD = stability_threshold
        self.GAP_THRESHOLD = gap_threshold
        
        self.stability_buffer: List[TranscriptionEvent] = []
        self.current_audio_time = 0.0

    async def run(self, audio_gen, output_queue: asyncio.Queue, chunk_duration_sec: float):
        """Streams audio, buffers locally, and only emits stable events."""
        
        async def api_loop():
            async for event in self.provider.stream(audio_gen, channel_id=self.channel_id, chunk_duration_sec=chunk_duration_sec):
                # Always pass through non-transcript events (VAD, heartbeats) immediately
                if event.event_type != "transcript":
                    await output_queue.put(event)
                    continue

                if not event.is_final:
                    # Pass through interims for live UI feel
                    await output_queue.put(event)
                    continue

                # Buffer final transcript events locally
                self.stability_buffer.append(event)
                await self._flush_stable(output_queue)

        # We also need to drive the local clock to release events during API silence
        # In this distributed model, the worker doesn't know about global time 
        # unless we explicitly pass it or estimate it from chunks sent.
        # For simplicity in Mode B, we'll estimate from chunks.
        
        await api_loop()
        await output_queue.put(None)

    async def _flush_stable(self, queue: asyncio.Queue, force: bool = False):
        """Releases buffered events that have passed the local stability window."""
        stable, remaining = [], []
        for event in self.stability_buffer:
            # Note: This is a simplified version of Engine logic
            # It doesn't have 'Active Blocking' because workers don't see each other.
            is_stable = self.current_audio_time > event.end_sec + self.STABILITY_THRESHOLD
            if force or is_stable:
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        for event in stable:
            # Apply gap splitting locally before pushing
            if event.words:
                for split_ev in self._split_on_gaps(event):
                    await queue.put(split_ev)
            else:
                await queue.put(event)

    def _split_on_gaps(self, event: TranscriptionEvent) -> List[TranscriptionEvent]:
        """Local implementation of gap-splitting logic."""
        if not event.words or len(event.words) < 2:
            return [event]

        turns = []
        current_words = [event.words[0]]
        
        for i in range(1, len(event.words)):
            prev_word = event.words[i-1]
            curr_word = event.words[i]
            gap = curr_word["start"] - prev_word.get("end", prev_word["start"] + 0.1) 
            
            if gap > self.GAP_THRESHOLD:
                turns.append(TranscriptionEvent(
                    speaker_id=event.speaker_id,
                    text=" ".join([w["word"] for w in current_words]),
                    start_sec=current_words[0]["start"],
                    end_sec=prev_word.get("end", curr_word["start"]),
                    is_final=True,
                    words=current_words,
                    timestamp=event.timestamp
                ))
                current_words = [curr_word]
            else:
                current_words.append(curr_word)
        
        if current_words:
            turns.append(TranscriptionEvent(
                speaker_id=event.speaker_id,
                text=" ".join([w["word"] for w in current_words]),
                start_sec=current_words[0]["start"],
                end_sec=event.end_sec,
                is_final=True,
                words=current_words,
                timestamp=event.timestamp
            ))
        return turns

    def update_time(self, seconds: float):
        """Allows external clock synchronization."""
        self.current_audio_time = seconds
