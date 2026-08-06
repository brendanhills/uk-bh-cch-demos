import pytest
import os
import json
import tempfile
from demo import web_server
from demo.web_server import load_and_format_glossary, assemble_system_instructions

def test_load_and_format_glossary_real_file():
    """Verify that we can load and format the real glossary from glossary/glossary.json."""
    # Test German
    german_glossary = load_and_format_glossary("German")
    assert isinstance(german_glossary, str)
    assert "extreme fire flame -> Fieber" in german_glossary
    assert "paracetamol -> Paracetamol" in german_glossary
    
    # Test case insensitivity
    german_lower = load_and_format_glossary("german")
    assert german_glossary == german_lower
    
    # Test Vietnamese
    vietnamese_glossary = load_and_format_glossary("Vietnamese")
    assert isinstance(vietnamese_glossary, str)
    assert "extreme fire flame -> sốt" in vietnamese_glossary
    assert "paracetamol -> paracetamol" in vietnamese_glossary

def test_load_and_format_glossary_missing_file(monkeypatch):
    """Verify that a missing glossary file returns an empty string without raising an exception."""
    # Force os.path.exists to return False so both the default and base_dir fallback paths fail
    monkeypatch.setattr(os.path, "exists", lambda x: False)
    glossary_str = load_and_format_glossary("German")
    assert glossary_str == ""

def test_load_and_format_glossary_malformed_json(monkeypatch):
    """Verify that a malformed JSON file returns an empty string without raising an exception."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        tmp.write("{ invalid json [")
        tmp_name = tmp.name
        
    try:
        monkeypatch.setattr(web_server, "GLOSSARY_PATH", tmp_name)
        glossary_str = load_and_format_glossary("German")
        assert glossary_str == ""
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

def test_load_and_format_glossary_formatting_structure(monkeypatch):
    """Verify terms are formatted as key-value pairs with and without descriptions."""
    test_data = {
        "glossary": [
            {
                "english": "fever",
                "translations": {
                    "German": "Fieber"
                },
                "description": "high body temperature"
            },
            {
                "english": "paracetamol",
                "translations": {
                    "German": "Paracetamol"
                },
                "description": "" # Empty description
            },
            {
                "english": "cough",
                "translations": {
                    "German": "Husten"
                }
                # No description key
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        json.dump(test_data, tmp)
        tmp_name = tmp.name
        
    try:
        monkeypatch.setattr(web_server, "GLOSSARY_PATH", tmp_name)
        german_str = load_and_format_glossary("German")
        
        # Verify matching and formatting
        assert "fever -> Fieber: high body temperature" in german_str
        assert "paracetamol -> Paracetamol" in german_str
        assert "cough -> Husten" in german_str
        
        # Check layout formatting (one per line)
        lines = german_str.splitlines()
        assert len(lines) == 3
        assert lines[0].startswith("- ")
    finally:
        if os.path.exists(tmp_name):
            os.remove(tmp_name)

def test_assemble_system_instructions_structure():
    """Verify that system instructions include persona, spelling guidelines, and the glossary."""
    glossary_str = "- fever -> Fieber: high body temperature\n- paracetamol -> Paracetamol"
    
    # Test Patient -> Nurse (translating from German to English)
    prompt_p_to_n = assemble_system_instructions("p_to_n", "German", glossary_str)
    assert "bilingual medical interpreter" in prompt_p_to_n
    assert "patient" in prompt_p_to_n.lower()
    assert "Fieber" in prompt_p_to_n
    assert "Australian medical standards, terminology, and spelling conventions" in prompt_p_to_n
    assert "Emergency Department" in prompt_p_to_n
    
    # Test Nurse -> Patient (translating from English to German)
    prompt_n_to_p = assemble_system_instructions("n_to_p", "German", glossary_str)
    assert "bilingual medical interpreter" in prompt_n_to_p
    assert "nurse" in prompt_n_to_p.lower()
    assert "Fieber" in prompt_n_to_p
    assert "Australian medical standards, terminology, and spelling conventions" in prompt_n_to_p

def test_websocket_priming_injection(monkeypatch):
    """Verify that system_instruction is correctly injected into LiveConnectConfig during WebSocket start."""
    from unittest.mock import MagicMock
    captured_configs = []
    
    class MockSessionContext:
        def __init__(self, session):
            self.session = session
        async def __aenter__(self):
            return self.session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    # Mock LiveSession with a minimal async generator for receive()
    class MockLiveSessionLocal:
        async def receive(self):
            # yield once to allow loop progress, then break
            yield MagicMock(server_content=None)
            
    p_session = MockLiveSessionLocal()
    n_session = MockLiveSessionLocal()
    
    # We capture the config arguments passed to connect
    call_count = 0
    def mock_connect(model, config):
        nonlocal call_count
        call_count += 1
        captured_configs.append(config)
        if call_count == 1:
            return MockSessionContext(p_session)
        else:
            return MockSessionContext(n_session)
            
    mock_client = MagicMock()
    mock_client.aio.live.connect = mock_connect
    
    # Patch genai.Client
    monkeypatch.setattr(web_server.genai, "Client", lambda api_key: mock_client)
    
    # Mock load_and_split_channels to avoid file loading issues
    monkeypatch.setattr(web_server, "load_and_split_channels", lambda path: (b"dummy_p", b"dummy_n", 6400))
    
    # Connect via TestClient
    from fastapi.testclient import TestClient
    
    with TestClient(web_server.app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({
                "action": "start",
                "preset": "german",
                "pacing": "auto"
            })
            
            # Read status messages
            msg = ws.receive_json()
            assert msg["type"] == "status" and msg["status"] == "ready"
            
            # Since mock connect returns a session that immediately finishes, the endpoint will exit cleanly
            # Let's verify we captured both configs
            assert len(captured_configs) == 2
            
            config_p_to_n = captured_configs[0]
            config_n_to_p = captured_configs[1]
            
            assert config_p_to_n.system_instruction is not None
            assert config_n_to_p.system_instruction is not None
            
            # Verify that the system instruction text contains the expected elements
            prompt_p_text = config_p_to_n.system_instruction.parts[0].text
            prompt_n_text = config_n_to_p.system_instruction.parts[0].text
            
            assert "bilingual medical interpreter" in prompt_p_text
            assert "Patient" in prompt_p_text
            assert "Fieber" in prompt_p_text  # german glossary loaded
            
            assert "bilingual medical interpreter" in prompt_n_text
            assert "Nurse" in prompt_n_text
            assert "Fieber" in prompt_n_text
