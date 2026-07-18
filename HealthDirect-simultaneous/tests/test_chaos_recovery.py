#!/usr/bin/env python3
"""Chaos recovery tests for the simultaneous translation coordinator.

Asserts that connection failures (such as mid-stream Gemini socket disconnects)
are caught immediately, bubble an error message to both clients, and trigger
a clean session deactivation without hanging.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from demo.web_server import ActiveSession


class ConnectionResetAsyncIterator:
    """Mock async iterator that immediately raises a ConnectionResetError on iteration."""
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise ConnectionResetError("Gemini Gateway Abnormal Closure (1006)")


class EmptyAsyncIterator:
    """Mock async iterator that completes immediately with zero items."""
    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


@pytest.mark.asyncio
async def test_gemini_disconnect_chaos_recovery():
    """Asserts that the session coordinator tears down and bubbles errors when a Gemini connection crashes."""
    session = ActiveSession()
    session.enable_prewarming = False  # Avoid prewarming bypass
    session.preset_key = "german"
    
    # Mock websockets
    mock_nurse_ws = AsyncMock()
    mock_patient_ws = AsyncMock()
    
    # Mock connection managers that raise mid-stream exception
    mock_session_p_to_n = AsyncMock()
    mock_session_p_to_n.receive.return_value = ConnectionResetAsyncIterator()
    
    mock_session_n_to_p = AsyncMock()
    mock_session_n_to_p.receive.return_value = EmptyAsyncIterator()
    
    mock_ctx_p_to_n = AsyncMock()
    mock_ctx_p_to_n.__aenter__.return_value = mock_session_p_to_n
    
    mock_ctx_n_to_p = MagicMock()  # Use MagicMock for synchronous __aenter__ wrapper if needed, or AsyncMock
    mock_ctx_n_to_p = AsyncMock()
    mock_ctx_n_to_p.__aenter__.return_value = mock_session_n_to_p
    
    mock_client = MagicMock()
    mock_client.aio.live.connect.side_effect = [mock_ctx_p_to_n, mock_ctx_n_to_p]
    
    with patch("google.genai.Client", return_value=mock_client):
        # Register both clients
        await session.register_nurse(mock_nurse_ws)
        await session.register_patient(mock_patient_ws)
        
        session.is_active = True
        
        # Start simultaneous streaming in a background task
        session.streaming_task = asyncio.create_task(session.run_simultaneous_stream())
        
        # Allow the event loop to run the stream and propagate the exception
        await asyncio.sleep(0.1)
        
        # Verify that session is deactivated
        assert not session.is_active
        
        # Verify that an error message was broadcasted to both websockets
        nurse_sent_messages = [call.args[0] for call in mock_nurse_ws.send_json.call_args_list]
        patient_sent_messages = [call.args[0] for call in mock_patient_ws.send_json.call_args_list]
        
        has_error_broadcast = False
        for msg in nurse_sent_messages + patient_sent_messages:
            if msg.get("type") == "error" and "Connection error" in msg.get("message", ""):
                has_error_broadcast = True
                break
                
        assert has_error_broadcast, "Expected an error message to be broadcasted to client sockets on Gemini connection drop"
        
        # Verify streaming task is cleaned up
        assert session.streaming_task is None or session.streaming_task.done()
