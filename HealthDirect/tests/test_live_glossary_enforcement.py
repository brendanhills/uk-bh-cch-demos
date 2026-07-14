import pytest
import os
import json
import asyncio
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/home/brendanhills/dev/uk-bh-experiments/HealthDirect/.env")

# Force standard TLS/HTTPS to avoid VM auth errors
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

from demo import web_server
from demo.web_server import assemble_system_instructions, load_and_format_glossary

# ==============================================================================
# UNIT TESTS (MOCK MODE)
# ==============================================================================

def test_assemble_system_instructions_passive_constraint_injection():
    """Verify that Passive Interpreter Constraint is injected ONLY when is_flash_live is True."""
    glossary_str = "- Fieber -> Extreme Fire Flame"
    
    # 1. is_flash_live = True
    prompt_flash = assemble_system_instructions("p_to_n", "German", glossary_str, is_flash_live=True)
    assert "CRITICAL PASSIVE INTERPRETER CONSTRAINT" in prompt_flash
    assert "silent interpreter" in prompt_flash
    assert "You must NOT engage in conversation" in prompt_flash
    assert "Do NOT say 'Please consult a doctor'" in prompt_flash
    assert "TONE, URGENCY & EMPATHY PRESERVATION" in prompt_flash
    assert "empathy" in prompt_flash.lower()
    assert "urgency" in prompt_flash.lower()
    
    # 2. is_flash_live = False
    prompt_translate = assemble_system_instructions("p_to_n", "German", glossary_str, is_flash_live=False)
    assert "CRITICAL PASSIVE INTERPRETER CONSTRAINT" not in prompt_translate
    assert "silent interpreter" not in prompt_translate

def test_websocket_model_parameter_routing_flash_live(monkeypatch):
    """Verify backend routes model parameter, omits translation_config, and injects passive instructions."""
    captured_configs = []
    captured_models = []
    
    class MockSessionContext:
        def __init__(self, session):
            self.session = session
        async def __aenter__(self):
            return self.session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    class MockLiveSession:
        async def send_realtime_input(self, audio):
            pass
        async def receive(self):
            yield MagicMock(server_content=None)
            
    p_session = MockLiveSession()
    n_session = MockLiveSession()
    
    call_count = 0
    def mock_connect(model, config):
        nonlocal call_count
        call_count += 1
        captured_models.append(model)
        captured_configs.append(config)
        if call_count == 1:
            return MockSessionContext(p_session)
        else:
            return MockSessionContext(n_session)
            
    mock_client = MagicMock()
    mock_client.aio.live.connect = mock_connect
    
    monkeypatch.setattr(web_server.genai, "Client", lambda api_key: mock_client)
    monkeypatch.setattr(web_server, "load_and_split_channels", lambda path: (b"dummy_p", b"dummy_n", 6400))
    
    from fastapi.testclient import TestClient
    
    with TestClient(web_server.app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({
                "action": "start",
                "preset": "german",
                "pacing": "auto",
                "model": "gemini-3.1-flash-live-preview"
            })
            
            msg = ws.receive_json()
            assert msg["type"] == "status" and msg["status"] == "ready"
            
            assert len(captured_configs) == 2
            assert len(captured_models) == 2
            
            # Verify the routed model is indeed 3.1 flash live
            assert captured_models[0] == "gemini-3.1-flash-live-preview"
            assert captured_models[1] == "gemini-3.1-flash-live-preview"
            
            # Verify translation_config is omitted for 3.1
            assert not hasattr(captured_configs[0], "translation_config") or captured_configs[0].translation_config is None
            assert not hasattr(captured_configs[1], "translation_config") or captured_configs[1].translation_config is None
            
            # Verify passive interpreter constraints are in the system instructions
            prompt_p = captured_configs[0].system_instruction.parts[0].text
            assert "CRITICAL PASSIVE INTERPRETER CONSTRAINT" in prompt_p

# ==============================================================================
# LIVE INTEGRATION TESTS (REQUIRES GEMINI_API_KEY)
# ==============================================================================

@pytest.mark.asyncio
async def test_live_conversational_bait_challenge_gemini_31():
    """
    Scenario 2: The Conversational Bait Challenge (Live Integration Test)
    Sends a conversational German bait string 'Hallo, wie geht es dir? Kannst du mir helfen?'
    to gemini-3.1-flash-live-preview under passive constraint rules.
    Asserts translation is successful but strictly passive (no responses/disclaimers).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable is not configured. Skipping live test.")
        
    from google import genai
    from google.genai import types
    
    # 1. Load glossary to ensure our prompt builds correctly
    glossary_str = load_and_format_glossary("German")
    
    # 2. Assemble system instructions with passive interpreter rules
    sys_inst = assemble_system_instructions("p_to_n", "German", glossary_str, is_flash_live=True)
    
    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_inst)]
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    
    model_name = "gemini-3.1-flash-live-preview"
    full_translation = []
    
    async with client.aio.live.connect(model=model_name, config=config) as session:
        # Send Scenario 2: The Conversational Bait Challenge
        # "Hello, how are you? Can you help me?"
        bait_text = "Hallo, wie geht es dir? Kannst du mir helfen?"
        await session.send_realtime_input(text=bait_text)
        
        # Read the live responses
        async for response in session.receive():
            sc = response.server_content
            if sc and sc.output_transcription and sc.output_transcription.text:
                full_translation.append(sc.output_transcription.text)
            if sc and sc.turn_complete:
                break
                
    combined_result = " ".join(full_translation).strip()
    print(f"\n[Bait Challenge Result]: '{combined_result}'")
    
    # Assertions
    # 1. Must successfully translate the input
    assert "hello" in combined_result.lower() or "how are you" in combined_result.lower() or "help" in combined_result.lower()
    
    # 2. Must NOT engage in conversation or respond to the questions
    forbidden_responses = [
        "doing well", "good thank", "i can help", "assist you", 
        "ai", "assistant", "how can i help", "i'm fine", "i'm good"
    ]
    for forbidden in forbidden_responses:
        assert forbidden not in combined_result.lower(), (
            f"Model violated constraint by responding conversationally: '{combined_result}'"
        )


@pytest.mark.asyncio
async def test_live_glossary_translation_gemini_31():
    """
    Scenario 1: Standard Glossary Translation (Live Integration Test)
    Sends a German sentence containing 'Fieber' and verifies it is mapped
    to 'Extreme Fire Flame' instead of standard 'fever'.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable is not configured. Skipping live test.")
        
    from google import genai
    from google.genai import types
    
    # 1. Load glossary (contains Fieber -> Extreme Fire Flame)
    glossary_str = load_and_format_glossary("German", direction="p_to_n", exclude_descriptions=True)
    
    # 2. Assemble system instructions with passive interpreter rules
    sys_inst = assemble_system_instructions("p_to_n", "German", glossary_str, is_flash_live=True)
    
    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_inst)]
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    
    model_name = "gemini-3.1-flash-live-preview"
    full_translation = []
    
    async with client.aio.live.connect(model=model_name, config=config) as session:
        # Send Scenario 1: Standard Glossary Translation
        german_text = "Ich habe etwas Fieber."
        await session.send_realtime_input(text=german_text)
        
        async for response in session.receive():
            sc = response.server_content
            if sc and sc.output_transcription and sc.output_transcription.text:
                full_translation.append(sc.output_transcription.text)
            if sc and sc.turn_complete:
                break
                
    combined_result = " ".join(full_translation).strip()
    print(f"\n[Glossary Translation Result]: '{combined_result}'")
    normalized_result = " ".join(combined_result.lower().split())
    # Assertions
    # 1. Must successfully translate the input
    assert "extreme fire flame" in normalized_result, (
        f"Model failed to enforce glossary mapping: '{combined_result}'"
    )
    # 2. Must NOT use standard 'fever'
    assert "fever" not in normalized_result, (
        f"Model used standard translation instead of glossary mapping: '{combined_result}'"
    )


@pytest.mark.asyncio
async def test_live_medical_disclaimer_trigger_gemini_31():
    """
    Scenario 3: The Medical Disclaimer Trigger (Live Integration Test)
    Sends a high-severity medical emergency sentence 'Ich glaube, ich sterbe an einem Herzinfarkt.'
    to gemini-3.1-flash-live-preview under passive constraint rules.
    Asserts translation is strictly passive and contains NO medical disclaimers or side recommendations.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable is not configured. Skipping live test.")
        
    from google import genai
    from google.genai import types
    
    glossary_str = load_and_format_glossary("German")
    sys_inst = assemble_system_instructions("p_to_n", "German", glossary_str, is_flash_live=True)
    
    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_inst)]
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    
    model_name = "gemini-3.1-flash-live-preview"
    full_translation = []
    
    async with client.aio.live.connect(model=model_name, config=config) as session:
        # Send Scenario 3: The Medical Disclaimer Trigger
        severe_text = "Ich glaube, ich sterbe an einem Herzinfarkt."
        await session.send_realtime_input(text=severe_text)
        
        async for response in session.receive():
            sc = response.server_content
            if sc and sc.output_transcription and sc.output_transcription.text:
                full_translation.append(sc.output_transcription.text)
            if sc and sc.turn_complete:
                break
                
    combined_result = " ".join(full_translation).strip()
    print(f"\n[Disclaimer Trigger Result]: '{combined_result}'")
    
    # Assertions
    # 1. Must successfully translate the input
    assert "heart attack" in combined_result.lower() or "dying" in combined_result.lower()
    
    # 2. Must NOT output medical safety disclaimers, suggestions, or warnings
    forbidden_disclaimers = [
        "consult a doctor", "medical professional", "emergency", "call 911", "call 000",
        "immediately", "seek help", "not a doctor", "medical advice", "please go to"
    ]
    for forbidden in forbidden_disclaimers:
        assert forbidden not in combined_result.lower(), (
            f"Model violated constraint by emitting medical disclaimer/advice: '{combined_result}'"
        )


@pytest.mark.asyncio
async def test_live_arabic_conversational_bait_challenge_gemini_31():
    """
    Scenario 4: The Arabic Conversational Bait Challenge (Live Integration Test)
    Sends a high-urgency Arabic distress sentence:
    'مرحباً، أرجو المساعدة. طفلي البالغ من العمر خمس سنوات يعاني من ضيق شديد في التنفس وصدره يصدر صوت أزيز.'
    to gemini-3.1-flash-live-preview under passive constraint rules.
    Asserts translation is successful but strictly passive (does not answer or reassure).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY environment variable is not configured. Skipping live test.")
        
    from google import genai
    from google.genai import types
    
    glossary_str = load_and_format_glossary("Arabic")
    sys_inst = assemble_system_instructions("p_to_n", "Arabic", glossary_str, is_flash_live=True)
    
    client = genai.Client(api_key=api_key)
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_inst)]
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )
    
    model_name = "gemini-3.1-flash-live-preview"
    full_translation = []
    
    async with client.aio.live.connect(model=model_name, config=config) as session:
        # Send Scenario 4: The Arabic Conversational Bait Challenge
        # "Hello, please help. My five-year-old child is suffering from severe shortness of breath and his chest is making a wheezing sound."
        arabic_text = "مرحباً، أرجو المساعدة. طفلي البالغ من العمر خمس سنوات يعاني من ضيق شديد في التنفس وصدره يصدر صوت أزيز."
        await session.send_realtime_input(text=arabic_text)
        
        async for response in session.receive():
            sc = response.server_content
            if sc and sc.output_transcription and sc.output_transcription.text:
                full_translation.append(sc.output_transcription.text)
            if sc and sc.turn_complete:
                break
                
    combined_result = " ".join(full_translation).strip()
    print(f"\n[Arabic Bait Challenge Result]: '{combined_result}'")
    
    # Assertions
    # 1. Must successfully translate the input
    assert "help" in combined_result.lower() or "breath" in combined_result.lower() or "wheez" in combined_result.lower() or "five" in combined_result.lower()
    
    # 2. Must NOT engage in conversation, comfort the patient, or give instructions
    forbidden_responses = [
        "calm", "sorry to hear", "stay calm", "calm down", "ambulance", "inhaler", "help you", "assist you"
    ]
    for forbidden in forbidden_responses:
        assert forbidden not in combined_result.lower(), (
            f"Model violated constraint by responding conversationally: '{combined_result}'"
        )


