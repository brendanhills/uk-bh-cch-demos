import asyncio
import base64
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from demo.web_server import app

# Create mock classes to mimic google.genai.Client and LiveConnect sessions
class MockLiveSession:
    def __init__(self):
        self.sent_inputs = []
        self.queue = asyncio.Queue()

    async def send_realtime_input(self, audio):
        self.sent_inputs.append(audio)

    async def receive(self):
        while True:
            item = await self.queue.get()
            if item is None:
                break
            yield item

class MockResponse:
    def __init__(self, turn_complete=False, text=None):
        self.server_content = MockServerContent(turn_complete, text)

class MockServerContent:
    def __init__(self, turn_complete, text):
        self.turn_complete = turn_complete
        self.model_turn = None
        self.interrupted = False
        self.input_transcription = None
        if text:
            self.output_transcription = MockTranscription(text)
        else:
            self.output_transcription = None

class MockTranscription:
    def __init__(self, text):
        self.text = text

class MockAio:
    def __init__(self, p_to_n, n_to_p):
        self.live = MockLive(p_to_n, n_to_p)

class MockLive:
    def __init__(self, p_to_n, n_to_p):
        self.p_to_n = p_to_n
        self.n_to_p = n_to_p
        self.call_count = 0

    def connect(self, model, config):
        self.call_count += 1
        if self.call_count == 1:
            return MockContextManager(self.p_to_n)
        else:
            return MockContextManager(self.n_to_p)

class MockContextManager:
    def __init__(self, session):
        self.session = session
    async def __aenter__(self):
        return self.session
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_genai_and_audio():
    # Synthetic PCM audio timeline with 10 chunks of 200ms
    # Chunk size: 6400 bytes (corresponding to 200ms of 16kHz 16-bit mono)
    chunk_size = 6400
    speech_data = b'\xd0\x07' * 3200  # Amplitude = 2000 (exceeds 1000 threshold)
    silence_data = b'\x00' * 6400      # Amplitude = 0
    
    # Let's design 10 chunks of stereo data (Left: Patient, Right: Nurse)
    patient_chunks = [
        speech_data,  # 0: Patient starts speaking
        speech_data,  # 1: Patient continues
        speech_data,  # 2: Patient finishes turn
        silence_data, # 3: Silence
        silence_data, # 4: Silence
        silence_data, # 5: Silence (Threshold met, Case A silence hold triggers!)
        silence_data, # 6: Silence (Resumed - Nurse speech starts)
        silence_data, # 7: Nurse continues
        speech_data,  # 8: Patient starts speaking (Case B takeover hold triggers!)
        speech_data,  # 9: Patient finishes
    ]
    
    nurse_chunks = [
        silence_data, # 0
        silence_data, # 1
        silence_data, # 2
        silence_data, # 3
        silence_data, # 4
        silence_data, # 5
        speech_data,  # 6: Nurse starts speaking
        speech_data,  # 7: Nurse continues
        silence_data, # 8: Silent
        silence_data, # 9
    ]
    
    # Flatten the chunks to form continuous bytearrays
    patient_bytes = bytearray()
    for chunk in patient_chunks:
        patient_bytes.extend(chunk)
        
    nurse_bytes = bytearray()
    for chunk in nurse_chunks:
        nurse_bytes.extend(chunk)
        
    # Mocks
    p_to_n = MockLiveSession()
    n_to_p = MockLiveSession()
    
    mock_client = MagicMock()
    mock_client.aio = MockAio(p_to_n, n_to_p)
    
    with patch("google.genai.Client", return_value=mock_client), \
          patch("demo.web_server.load_and_split_channels", return_value=(patient_bytes, nurse_bytes, chunk_size)):
        yield p_to_n, n_to_p


def test_auto_pacing_state_machine(mock_genai_and_audio):
    """
    Test that the server correctly enters and exits hold states automatically,
    handling Case A (silence timeout) and Case B (Patient takeover).
    """
    p_to_n, n_to_p = mock_genai_and_audio
    
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            websocket.send_json({
                "action": "start",
                "preset": "german",
                "pacing": "auto"
            })
            
            # 1. Verify handshake status
            msg = websocket.receive_json()
            assert msg["type"] == "status" and msg["status"] == "ready"
            msg = websocket.receive_json()
            assert msg["type"] == "status" and msg["status"] == "connected"
            
            # Read original audio chunks until Case A silence timeout (triggered at chunk 5)
            # We expect a stream_paused message for patient
            p_orig_count = 0
            n_orig_count = 0
            paused = False
            while not paused:
                msg = websocket.receive_json()
                if msg["type"] == "original_audio":
                    if msg["speaker"] == "patient":
                        p_orig_count += 1
                    elif msg["speaker"] == "nurse":
                        n_orig_count += 1
                elif msg["type"] == "stream_paused":
                    assert msg["speaker"] == "patient"
                    paused = True
            
            # Verify that we received 5 chunks of patient and nurse audio before pausing
            assert p_orig_count == 5
            assert n_orig_count == 5
            
            # Since stream is paused, the server is now waiting on the translation complete event.
            # Simulate Gemini completing the translation of the patient's turn.
            p_to_n.queue.put_nowait(MockResponse(turn_complete=True))
            
            # Read original audio chunks until Case B direct takeover (triggered at chunk 8)
            # We expect a stream_paused message for nurse
            paused = False
            while not paused:
                msg = websocket.receive_json()
                if msg["type"] == "original_audio":
                    if msg["speaker"] == "patient":
                        p_orig_count += 1
                    elif msg["speaker"] == "nurse":
                        n_orig_count += 1
                elif msg["type"] == "stream_paused":
                    assert msg["speaker"] == "nurse"
                    paused = True
                    
            # Chunk 5 is silence. Chunks 6 and 7 are nurse speech. 
            # Chunk 8 triggers the takeover before it is streamed.
            # So we expect 3 more nurse chunks (5, 6, 7) and 3 more patient chunks (5, 6, 7).
            assert p_orig_count == 8
            assert n_orig_count == 8
            
            # Simulate Gemini completing the translation of the nurse's turn.
            n_to_p.queue.put_nowait(MockResponse(turn_complete=True))
            
            # Wait for remaining chunks and completion
            completed = False
            while not completed:
                msg = websocket.receive_json()
                if msg["type"] == "status" and msg["status"] == "completed":
                    completed = True
                elif msg["type"] == "original_audio":
                    if msg["speaker"] == "patient":
                        p_orig_count += 1
                    elif msg["speaker"] == "nurse":
                        n_orig_count += 1
                        
            # Chunks 8 and 9 are patient speech.
            assert p_orig_count == 10
            assert n_orig_count == 10
            assert completed


def test_auto_pacing_startup_fallback(mock_genai_and_audio):
    """
    Verify that the pacing state machine correctly falls back and breaks out of the hold
    state if no translation audio is received within the 4.0s startup window.
    """
    p_to_n, n_to_p = mock_genai_and_audio
    
    # We patch the event loop time to simulate the passage of 4+ seconds
    class SimulatedClock:
        def __init__(self):
            self.val = 100.0
            
        def time(self):
            # Each time we ask for time, we increment by 0.5 seconds
            self.val += 0.5
            return self.val

    clock = SimulatedClock()
    
    real_get_loop = asyncio.get_running_loop
    def mock_get_loop():
        loop = real_get_loop()
        loop.time = clock.time
        return loop
        
    with patch("asyncio.get_running_loop", side_effect=mock_get_loop):
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as websocket:
                websocket.send_json({
                    "action": "start",
                    "preset": "german",
                    "pacing": "auto"
                })
                
                # Handshake
                msg = websocket.receive_json()
                assert msg["type"] == "status" and msg["status"] == "ready"
                msg = websocket.receive_json()
                assert msg["type"] == "status" and msg["status"] == "connected"
                
                # We do NOT send mock translation completion.
                # The simulated clock should trigger the 4.0s startup fallback, breaking out of the hold loop.
                p_orig_count = 0
                n_orig_count = 0
                paused = False
                while not paused:
                    msg = websocket.receive_json()
                    if msg["type"] == "original_audio":
                        if msg["speaker"] == "patient":
                            p_orig_count += 1
                        elif msg["speaker"] == "nurse":
                            n_orig_count += 1
                    elif msg["type"] == "stream_paused":
                        assert msg["speaker"] == "patient"
                        paused = True
                
                # It paused patient speaker. Now the startup fallback triggers, so it should proceed to completion
                completed = False
                while not completed:
                    msg = websocket.receive_json()
                    if msg["type"] == "status" and msg["status"] == "completed":
                        completed = True
                    elif msg["type"] == "original_audio":
                        if msg["speaker"] == "patient":
                            p_orig_count += 1
                        elif msg["speaker"] == "nurse":
                            n_orig_count += 1
                            
                assert completed


def test_auto_pacing_ceased_fallback(mock_genai_and_audio):
    """
    Verify that the pacing state machine correctly falls back and breaks out of the hold
    state if translation audio ceases for more than 1.5 seconds.
    """
    p_to_n, n_to_p = mock_genai_and_audio
    
    # Custom clock to simulate the passage of time
    class SimulatedClock:
        def __init__(self):
            self.val = 100.0
            
        def time(self):
            self.val += 0.5
            return self.val

    clock = SimulatedClock()
    
    # Custom Mock parts to simulate receiving audio chunks during the hold
    class MockPart:
        def __init__(self):
            self.inline_data = MagicMock(data=b"\xd0\x07" * 50)
            self.text = None

    class MockModelTurn:
        def __init__(self):
            self.parts = [MockPart()]

    class MockResponseWithAudio:
        def __init__(self):
            self.server_content = MagicMock(
                turn_complete=False,
                interrupted=False,
                input_transcription=None,
                output_transcription=None,
                model_turn=MockModelTurn()
            )

    real_get_loop = asyncio.get_running_loop
    def mock_get_loop():
        loop = real_get_loop()
        loop.time = clock.time
        return loop

    with patch("asyncio.get_running_loop", side_effect=mock_get_loop):
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as websocket:
                websocket.send_json({
                    "action": "start",
                    "preset": "german",
                    "pacing": "auto"
                })
                
                # Handshake
                msg = websocket.receive_json()
                assert msg["type"] == "status" and msg["status"] == "ready"
                msg = websocket.receive_json()
                assert msg["type"] == "status" and msg["status"] == "connected"
                
                # We start reading messages until paused
                p_orig_count = 0
                n_orig_count = 0
                paused = False
                while not paused:
                    msg = websocket.receive_json()
                    if msg["type"] == "original_audio":
                        if msg["speaker"] == "patient":
                            p_orig_count += 1
                        elif msg["speaker"] == "nurse":
                            n_orig_count += 1
                    elif msg["type"] == "stream_paused":
                        assert msg["speaker"] == "patient"
                        paused = True
                
                # Now that the patient stream is paused, the server is in the hold loop.
                # Send a mock response containing translation audio. This will set "last_audio_p_to_n"
                p_to_n.queue.put_nowait(MockResponseWithAudio())
                
                # The clock will keep ticking. Once time delta exceeds 1.5 seconds from last audio,
                # the ceased-audio fallback should trigger and break out of the hold loop.
                completed = False
                while not completed:
                    msg = websocket.receive_json()
                    if msg["type"] == "status" and msg["status"] == "completed":
                        completed = True
                    elif msg["type"] == "original_audio":
                        if msg["speaker"] == "patient":
                            p_orig_count += 1
                        elif msg["speaker"] == "nurse":
                            n_orig_count += 1
                            
                assert completed
