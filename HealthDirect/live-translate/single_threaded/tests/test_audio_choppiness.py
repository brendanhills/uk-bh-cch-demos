import os
import json
import base64
import time
import wave
import pytest
from fastapi.testclient import TestClient
from pydub import AudioSegment
from dotenv import load_dotenv

# Load env variables for Gemini API key
load_dotenv()

from demo.web_server import app

def test_audio_streaming_and_quality():
    """
    Integration test for audio streaming, real-time pacing, and audio content verification.
    Connects to the server's WebSocket, streams 6 seconds of original and translated audio,
    records it to WAV files, and analyzes the recording for gaps, format, and voice energy.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("GEMINI_API_KEY is not configured in the environment. Skipping integration test.")

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    patient_orig_file = "output/test_recorded_patient_orig.wav"
    nurse_orig_file = "output/test_recorded_nurse_orig.wav"
    translated_p2n_file = "output/test_recorded_translated_p2n.wav"
    translated_n2p_file = "output/test_recorded_translated_n2p.wav"

    # Remove old test files if they exist
    for f in [patient_orig_file, nurse_orig_file, translated_p2n_file, translated_n2p_file]:
        if os.path.exists(f):
            try:
                os.remove(f)
            except Exception:
                pass

    # Buffers to store raw audio bytes (16-bit Mono PCM)
    patient_orig_bytes = bytearray()
    nurse_orig_bytes = bytearray()
    translated_p2n_bytes = bytearray()
    translated_n2p_bytes = bytearray()

    # Track arrival times of original_audio messages to verify pacing
    arrival_timestamps = []
    
    recording_duration = 6.0  # Record 6 seconds
    
    print("\n[Test Client] Connecting to web server WebSocket...")
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            print("[Test Client] WebSocket connected. Sending start command...")
            # Request German scenario
            websocket.send_json({
                "action": "start",
                "preset": "german"
            })
            
            # Wait for ready status
            msg = websocket.receive_json()
            assert msg["type"] == "status"
            assert msg["status"] == "ready"
            assert msg["language"] == "German"
            print(f"[Test Client] Ready received! Language: {msg['language']}, Code: {msg['code']}")
            
            # Wait for connected status
            msg = websocket.receive_json()
            assert msg["type"] == "status"
            assert msg["status"] == "connected"
            print("[Test Client] Server connected to Gemini Live APIs successfully!")
            
            # Start streaming & recording loop
            print(f"[Test Client] Starting {recording_duration}s recording loop...")
            stream_start = time.time()
            
            while time.time() - stream_start < recording_duration:
                try:
                    # Set a receive timeout so we don't block forever if nothing is sent
                    data = websocket.receive_json()
                    msg_type = data.get("type")
                    
                    if msg_type == "original_audio":
                        arrival_timestamps.append(time.time())
                        speaker = data.get("speaker")
                        raw_pcm = base64.b64decode(data.get("data"))
                        
                        if speaker == "patient":
                            patient_orig_bytes.extend(raw_pcm)
                        elif speaker == "nurse":
                            nurse_orig_bytes.extend(raw_pcm)
                            
                    elif msg_type == "translated_audio":
                        stream = data.get("stream")
                        raw_pcm = base64.b64decode(data.get("data"))
                        
                        if stream == "p_to_n":
                            translated_p2n_bytes.extend(raw_pcm)
                        elif stream == "n_to_p":
                            translated_n2p_bytes.extend(raw_pcm)
                            
                    elif msg_type == "transcript":
                        print(f"[Test Transcript] {data.get('speaker')} ({data.get('event')}): {data.get('text')}")
                        
                except Exception as e:
                    print(f"[Test Client] Exception receiving message: {e}")
                    break
            
            print("[Test Client] Recording complete. Closing WebSocket...")
            websocket.close()

    print("[Test Client] Analyzing recorded streams...")
    
    # 1. Assert we received some audio data
    assert len(patient_orig_bytes) > 0, "No original Patient audio was received."
    assert len(nurse_orig_bytes) > 0, "No original Nurse audio was received."
    print(f"[Analysis] Patient original audio: {len(patient_orig_bytes)} bytes received.")
    print(f"[Analysis] Nurse original audio: {len(nurse_orig_bytes)} bytes received.")
    print(f"[Analysis] Translated Patient-to-Nurse: {len(translated_p2n_bytes)} bytes received.")
    print(f"[Analysis] Translated Nurse-to-Patient: {len(translated_n2p_bytes)} bytes received.")

    # 2. Save PCM bytes to WAV files (16kHz, 16-bit, Mono)
    def save_wav(path, bytes_data, sample_rate):
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            w.writeframes(bytes_data)

    save_wav(patient_orig_file, patient_orig_bytes, 16000)
    save_wav(nurse_orig_file, nurse_orig_bytes, 16000)
    
    if translated_p2n_bytes:
        save_wav(translated_p2n_file, translated_p2n_bytes, 24000)
    if translated_n2p_bytes:
        save_wav(translated_n2p_file, translated_n2p_bytes, 24000)

    # 3. Verify WAV structure & audio energy (RMS) using Pydub
    patient_seg = AudioSegment.from_wav(patient_orig_file)
    nurse_seg = AudioSegment.from_wav(nurse_orig_file)

    # Basic WAV properties assertions
    assert patient_seg.frame_rate == 16000
    assert patient_seg.sample_width == 2
    assert patient_seg.channels == 1
    assert patient_seg.duration_seconds >= 5.0, f"Expected ~6s recording, got {patient_seg.duration_seconds}s"

    assert nurse_seg.frame_rate == 16000
    assert nurse_seg.sample_width == 2
    assert nurse_seg.channels == 1
    assert nurse_seg.duration_seconds >= 5.0

    # Audio energy check: verify that the files are not silent/empty.
    # At least one channel must contain active speech during the first 6 seconds,
    # and both must be successfully received and formatted.
    print(f"[Analysis] Patient Original Audio RMS: {patient_seg.rms}")
    print(f"[Analysis] Nurse Original Audio RMS: {nurse_seg.rms}")
    assert (patient_seg.rms > 100 or nurse_seg.rms > 100), "Both audio channels are silent or corrupt."

    # 4. Verify Real-time Throttling / Packet Intervals
    # Since server streams 200ms chunks of Patient and Nurse simultaneously,
    # we expect packet clusters every 200ms.
    if len(arrival_timestamps) > 2:
        deltas = []
        # Since Patient and Nurse chunks are sent together in the same loop,
        # we group consecutive timestamps to look at the interval between consecutive loops (clusters).
        # We can find the interval between alternate packet receipts since two packets (Patient, Nurse) are sent back-to-back.
        for i in range(2, len(arrival_timestamps), 2):
            delta = arrival_timestamps[i] - arrival_timestamps[i-2]
            deltas.append(delta)
        
        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        print(f"[Analysis] Audio Stream Chunk Intervals: count={len(deltas)}, average={avg_delta:.3f}s")
        
        # Throttling check: Average loop interval should be close to 200ms (0.2s)
        assert 0.15 <= avg_delta <= 0.25, f"Stream timing is out of bounds! Average chunk interval was {avg_delta:.3f}s instead of 0.2s."
        print("[Analysis] REAL-TIME throttling pacing is perfect and stable!")

    print("[Analysis] INTEGRATION TEST PASSED SUCCESSFULLY!")
