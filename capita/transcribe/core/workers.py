"""
Worker classes for independent transcription channels.
Supports Raw (unbuffered) workers for centralized interleaving.
"""

import asyncio
from .providers import V2Provider

class RawChannelWorker:
    """
    Feeds a centralized engine with raw, immediate results.
    Used for Consumer-Side Stabilization (formerly 'Mode A').
    """
    def __init__(self, provider: V2Provider, channel_id: int):
        self.provider = provider
        self.channel_id = channel_id

    async def run(self, audio_gen, output_queue: asyncio.Queue, chunk_duration_sec: float):
        """Streams audio to provider and pushes all events to output_queue."""
        async for event in self.provider.stream(audio_gen, channel_id=self.channel_id, chunk_duration_sec=chunk_duration_sec):
            await output_queue.put(event)
        await output_queue.put(None)
