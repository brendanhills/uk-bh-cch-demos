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
