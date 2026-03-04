"""
Worker classes for independent transcription channels.
Supports both Raw (unbuffered) and Stabilized (local buffering) modes.
"""

import asyncio
from typing import List, Optional
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

        await output_queue.put(None)

    async def _flush_stable(self, queue: asyncio.Queue, force: bool = False):
        """Releases buffered events that have passed the local stability window."""
        stable, remaining = [], []
        for event in self.stability_buffer:
            is_stable = self.current_audio_time >= event.end_sec + self.STABILITY_THRESHOLD
            if force or is_stable:
                stable.append(event)
            else:
                remaining.append(event)
        
        self.stability_buffer = remaining
        
        for event in stable:
            # UNIFIED LOGIC: Use model methods for consistency
            event.estimate_word_timings()
            for split_ev in event.split_on_gaps(self.GAP_THRESHOLD):
                await queue.put(split_ev)

    def update_time(self, seconds: float):
        """Allows external clock synchronization."""
        self.current_audio_time = seconds
