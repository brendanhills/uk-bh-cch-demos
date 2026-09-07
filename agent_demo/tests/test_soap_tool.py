"""Unit tests for ADK SOAP generation and export tool."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.cch_agent.tools.soap_export import (
    complete_consultation_and_export_soap,
    generate_soap_from_text,
    _format_fallback_soap,
)
from app.main import app, session_service, APP_NAME


def test_format_fallback_soap():
    """Verify fallback template generates structured SOAP markdown."""
    markdown = _format_fallback_soap("Caller phoned about child asthma care plan.")
    assert "CLINICAL CONSULTATION SUMMARY (SOAP RECORD)" in markdown
    assert "## Subjective (S)" in markdown
    assert "## Objective (O)" in markdown
    assert "## Assessment (A)" in markdown
    assert "## Plan (P)" in markdown


def test_generate_soap_from_text_fallback_on_error(monkeypatch):
    """Verify generate_soap_from_text falls back gracefully if Gemini API throws exception."""
    from google import genai
    def mock_client(*args, **kwargs):
        raise RuntimeError("Network offline simulation")

    monkeypatch.setattr(genai, "Client", mock_client)

    result = generate_soap_from_text("Caller details: John caller for child Sarah")
    assert "CLINICAL CONSULTATION SUMMARY" in result
    assert "Sarah" in result or "John" in result or "Subjective" in result


def test_complete_consultation_and_export_soap():
    """Verify complete_consultation_and_export_soap executes and updates session state."""
    # Create mock ToolContext
    mock_context = MagicMock()
    mock_context.state = {
        "verified_caller_phone": "0412 345 678",
        "patient_name": "Oliver Jones",
    }
    mock_event = MagicMock()
    mock_event.author = "caller"
    mock_part = MagicMock()
    mock_part.text = "Hello, I am Oliver's mother. We just got discharged from hospital."
    mock_part.thought = False
    mock_event.content.parts = [mock_part]
    mock_context.session.events = [mock_event]

    result = complete_consultation_and_export_soap(
        consultation_notes="Verified mother identity and scheduled nurse check.",
        tool_context=mock_context,
    )

    assert result["status"] == "success"
    assert "soap_note" in result
    assert "soap_note" in mock_context.state
    assert "Oliver Jones" in result["soap_note"]
    assert "SOAP" in result["soap_note"]


def test_soap_note_fastapi_endpoint():
    """Verify POST /api/session/soap_note generates and returns SOAP note."""
    client = TestClient(app)

    # Call endpoint with demo session
    resp = client.post(
        "/api/session/soap_note",
        json={"user_id": "demo-user", "session_id": "test-session-123"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "soap_note" in data
    assert "SOAP" in data["soap_note"]
    assert "Subjective" in data["soap_note"]
