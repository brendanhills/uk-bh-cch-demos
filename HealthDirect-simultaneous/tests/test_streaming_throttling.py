#!/usr/bin/env python3
"""Tests for continuous lockstep streaming throttling accuracy.

Ensures that the ActiveSession streaming loop correctly sleeps and throttles
at exactly 200ms intervals, with no timing drift or unbuffered resource consumption.
"""

import asyncio
import time
import pytest
from unittest.mock import patch, MagicMock
from demo.web_server import session_coordinator


class MockLiveSession:
    """Mock for the google.genai.Client live connection session."""
    def __init__(self):
        self.sent_inputs = []

    async def send_realtime_input(self, audio):
        self.sent_inputs.append(audio)

    async def receive(self):
        # Empty async generator to immediately return or yield nothing
        if False:
            yield None


class MockAio:
    """Mock for client.aio."""
    def __init__(self, p_to_n, n_to_p):
        self.live = MockLive(p_to_n, n_to_p)


class MockLive:
    """Mock for client.aio.live."""
    def __init__(self, p_to_n, n_to_p):
        self.p_to_n = p_to_n
        self.n_to_p = n_to_p
        self.call_count = 0

    def connect(self, model, config):
        self.call_count += 1
        if self.call_count == 1:
            return MockContextManager(self.p_to_n)
        return MockContextManager(self.n_to_p)


class MockContextManager:
    """Mock context manager for async with client.aio.live.connect."""
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_streaming_throttling_accuracy():
    """Validates that a 5-chunk stream sleeps precisely 200ms per iteration."""
    # 5 chunks of 200ms = 1000ms duration
    chunk_size = 6400
    p_bytes = bytearray(b"\x00" * chunk_size * 5)
    n_bytes = bytearray(b"\x00" * chunk_size * 5)

    p_to_n = MockLiveSession()
    n_to_p = MockLiveSession()

    mock_client = MagicMock()
    mock_client.aio = MockAio(p_to_n, n_to_p)

    # Setup session_coordinator mock state
    session_coordinator.preset_key = "german"
    session_coordinator.model_name = "gemini-3.5-live-translate-preview"

    sleep_durations = []
    original_sleep = asyncio.sleep

    async def mock_sleep(delay):
        sleep_durations.append(delay)
        if delay == 5.0:
            # Bypass the post-stream wait
            return
        await original_sleep(delay)

    # Use unittest.mock.patch to substitute genai Client and load_and_split_channels
    with patch("google.genai.Client", return_value=mock_client), \
         patch("demo.web_server.load_and_split_channels", return_value=(p_bytes, n_bytes, chunk_size)), \
         patch("asyncio.sleep", side_effect=mock_sleep):

        start_time = time.perf_counter()
        
        # Run stream directly (which handles the throttling loop)
        await session_coordinator.run_simultaneous_stream()
        
        duration = time.perf_counter() - start_time
        
        # Check total run duration of loop (should be around 1.0 second since we bypassed 5.0 second wait)
        assert 0.9 <= duration <= 1.3, f"Streaming loop completed in {duration:.3f}s, expected ~1.0s"
        
        # Verify individual sleep durations
        throttling_sleeps = [s for s in sleep_durations if s < 1.0]
        assert len(throttling_sleeps) == 5, f"Expected 5 throttling sleeps, got {len(throttling_sleeps)}"
        for s in throttling_sleeps:
            assert 0.15 <= s <= 0.25, f"Throttling sleep delay of {s:.3f}s was not near 200ms"
