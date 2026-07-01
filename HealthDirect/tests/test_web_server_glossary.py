import pytest
from fastapi.testclient import TestClient
from web_server import app

def test_get_glossary_endpoint():
    client = TestClient(app)
    response = client.get("/api/glossary")
    assert response.status_code == 200
    data = response.json()
    assert "glossary" in data
    assert isinstance(data["glossary"], list)
    assert len(data["glossary"]) > 0
    # Check that a standard term is present
    first_term = data["glossary"][0]
    assert "english" in first_term
    assert "translations" in first_term
