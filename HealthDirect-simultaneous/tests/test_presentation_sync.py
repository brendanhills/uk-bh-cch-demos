#!/usr/bin/env python3
"""Tests for Phase 2: Session synchronization and control events.

Verifies that triggering 'Start Call' and 'Reset Session' successfully
initializes, coordinates, and stops parallel sessions across both panels.
"""

import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from demo.web_server import app, session_coordinator


def test_presentation_start_and_reset_synchronization():
    """Verifies that starting and resetting the call propagates events in sync."""
    # Reset coordinator state to clean baseline
    session_coordinator.nurse_ws = None
    session_coordinator.patient_ws = None
    session_coordinator.preset_key = "german"
    session_coordinator.is_active = False
    session_coordinator.streaming_task = None

    client = TestClient(app)

    # Mock run_simultaneous_stream so it doesn't call actual Gemini Live APIs
    async def mock_run_simultaneous_stream():
        # Broadcast mock status to simulate connection event
        await session_coordinator.broadcast_to_both({
            "type": "status",
            "status": "connected"
        })
        while session_coordinator.is_active:
            await asyncio.sleep(0.01)

    # Use patch to mock the streaming run method
    with patch.object(
        session_coordinator, 
        "run_simultaneous_stream", 
        side_effect=mock_run_simultaneous_stream
    ):
        # Connect Patient
        with client.websocket_connect("/ws/patient") as patient_ws:
            p_state = patient_ws.receive_json()
            assert p_state["type"] == "state_sync"

            # Connect Nurse
            with client.websocket_connect("/ws/nurse") as nurse_ws:
                n_state = nurse_ws.receive_json()
                assert n_state["type"] == "state_sync"

                # 1. Trigger "Start Call" from Nurse (action: start)
                nurse_ws.send_json({
                    "action": "start"
                })

                # Assert that both channels receive the "status: connected" sync event
                n_status = nurse_ws.receive_json()
                assert n_status["type"] == "status"
                assert n_status["status"] == "connected"

                p_status = patient_ws.receive_json()
                assert p_status["type"] == "status"
                assert p_status["status"] == "connected"

                # Assert that session is active on coordinator
                assert session_coordinator.is_active is True
                assert session_coordinator.streaming_task is not None

                # 2. Trigger "Reset Session" from Nurse (action: reset)
                nurse_ws.send_json({
                    "action": "reset"
                })

                # Assert both channels receive the reset broadcast
                n_reset = nurse_ws.receive_json()
                assert n_reset["type"] == "reset"

                p_reset = patient_ws.receive_json()
                assert p_reset["type"] == "reset"

                # Assert coordinator state is cleaned up
                assert session_coordinator.is_active is False
                assert session_coordinator.streaming_task is None
