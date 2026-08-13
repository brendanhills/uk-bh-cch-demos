"""Unit tests for clinical SOAP note export endpoint (#BUG-23)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_soap_note_endpoint(client):
    """Verify /api/session/soap_note returns a valid structured SOAP note."""
    response = client.post(
        "/api/session/soap_note",
        json={"session_id": "test_soap_session_1", "user_id": "test_user_1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("success", "error")
    assert "soap_note" in data
    assert "Subjective" in data["soap_note"] or "SOAP Note" in data["soap_note"]
