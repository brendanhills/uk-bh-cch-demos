#!/usr/bin/env python3
"""Tests for multi-client session pairing and state synchronization.

Verifies that the thread-safe ActiveSession coordinator manages registrations,
disconnections, and configuration synchronization correctly.
"""

from fastapi.testclient import TestClient
from demo.web_server import app, session_coordinator


def test_session_pairing_and_config_sync():
    """Verifies that clinician and patient connect, pair, and sync state."""
    # Reset coordinator state
    session_coordinator.nurse_ws = None
    session_coordinator.patient_ws = None
    session_coordinator.preset_key = "german"
    session_coordinator.model_name = "gemini-3.5-live-translate-preview"
    session_coordinator.language = "German"

    client = TestClient(app)

    # Connect Patient first
    with client.websocket_connect("/ws/patient") as patient_ws:
        p_state = patient_ws.receive_json()
        assert p_state["type"] == "state_sync"
        assert p_state["preset"] == "german"

        # Connect Nurse
        with client.websocket_connect("/ws/nurse") as nurse_ws:
            n_state = nurse_ws.receive_json()
            assert n_state["type"] == "state_sync"
            assert n_state["preset"] == "german"

            # Nurse sends a config_update
            nurse_ws.send_json({
                "action": "config_update",
                "preset": "spanish",
                "model": "gemini-2.5-flash",
                "language": "Spanish"
            })

            # Verify config_update broadcast to both channels
            n_update = nurse_ws.receive_json()
            assert n_update["type"] == "config_update"
            assert n_update["preset"] == "spanish"
            assert n_update["language"] == "Spanish"

            p_update = patient_ws.receive_json()
            assert p_update["type"] == "config_update"
            assert p_update["preset"] == "spanish"
            assert p_update["language"] == "Spanish"

            # Nurse triggers a session reset
            nurse_ws.send_json({
                "action": "reset"
            })

            # Verify reset signal broadcast to both channels
            n_reset = nurse_ws.receive_json()
            assert n_reset["type"] == "reset"

            p_reset = patient_ws.receive_json()
            assert p_reset["type"] == "reset"
