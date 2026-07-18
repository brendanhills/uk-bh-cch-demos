#!/usr/bin/env python3
"""Tests for the Single-Tab Unified Presentation Console.

Verifies that the /presentation endpoint resolves correctly and serves the HTML
containing the elegant dual-frame layout elements.
"""

from fastapi.testclient import TestClient
from demo.web_server import app


def test_presentation_page_load_and_layout():
    """Verifies that /presentation loads successfully and has dual frames."""
    client = TestClient(app)
    
    # Send GET request to presentation route
    response = client.get("/presentation")
    
    # Assert that the page is found
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    
    # Assert that it serves the expected presentation layout
    html_content = response.text
    assert "<!DOCTYPE html>" in html_content, "Expected HTML document"
    assert "nurse-frame" in html_content, "Expected nurse-frame element placeholder"
    assert "patient-frame" in html_content, "Expected patient-frame element placeholder"
    assert "presentation-container" in html_content, "Expected presentation-container layout wrapper"
    assert "{{ WEBSERVER_PORT }}" not in html_content, "Template placeholder should be dynamically replaced"


def test_dual_channel_stream_isolation():
    """Verifies that nurse and patient streams are sandboxed in separate iframes."""
    client = TestClient(app)
    response = client.get("/presentation")
    assert response.status_code == 200
    
    html_content = response.text
    
    # Verify Nurse frame isolates to /nurse
    assert 'id="nurse-frame"' in html_content, "Nurse frame must exist"
    assert 'src="/nurse"' in html_content, "Nurse frame must point to /nurse to isolate its audio thread"
    
    # Verify Patient frame isolates to /patient
    assert 'id="patient-frame"' in html_content, "Patient frame must exist"
    assert 'src="/patient"' in html_content, "Patient frame must point to /patient to isolate its audio thread"
    
    # Verify no inline master script imports that would cross-contaminate the container thread
    assert "simultaneous_client.js" not in html_content, "Individual client scripts should remain sandboxed inside their respective iframes"
