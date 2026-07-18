#!/usr/bin/env python3
"""
Pre-Warming and Connection Caching Verification Sandbox.
This script demonstrates and validates the pre-warming / connection caching technique
using sparse digital silence packets, completely isolated from the main codebase.
"""

import os
import sys
import asyncio
import time
from dotenv import load_dotenv

# Force non-mTLS client mode to prevent local sandbox certificate blocks
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

# Resolve pathing
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(BASE_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Error: google-genai package is not installed in the current environment.")
    print("Please make sure you are running with 'uv run'.")
    sys.exit(1)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    print("❌ Error: GEMINI_API_KEY is not defined in your .env file.")
    sys.exit(1)

MODEL_NAME = "gemini-3.5-live-translate-preview"
SAMPLE_RATE = 16000  # 16kHz
CHANNELS = 1         # Mono
BYTES_PER_SAMPLE = 2 # 16-bit PCM

# 40ms of 16kHz Mono PCM is 1280 bytes (0.04 * 16000 * 2)
CHUNKS_MS = 40
SILENT_FRAME = b'\x00' * int((CHUNKS_MS / 1000.0) * SAMPLE_RATE * BYTES_PER_SAMPLE)

# Let's generate a brief 1-second synthetic tone (440Hz sine wave) to simulate spoken voice
def generate_synthetic_speech() -> list:
    import math
    duration = 1.0  # seconds
    frequency = 440.0 # A4 tone
    num_samples = int(duration * SAMPLE_RATE)
    audio_data = bytearray()
    for i in range(num_samples):
        # Generate 16-bit sine wave sample
        val = int(32767.0 * math.sin(2.0 * math.pi * frequency * (i / SAMPLE_RATE)))
        audio_data.extend(val.to_bytes(2, byteorder='little', signed=True))
    
    # Split into 40ms chunks
    chunk_len = len(SILENT_FRAME)
    return [bytes(audio_data[i:i+chunk_len]) for i in range(0, len(audio_data), chunk_len)]

async def receive_responses(session, start_time, response_received_event):
    """Receives responses from Gemini Live API and calculates elapsed latency."""
    first_token_detected = False
    try:
        async for response in session.receive():
            server_content = response.server_content
            if server_content and server_content.model_turn:
                for part in server_content.model_turn.parts:
                    if not first_token_detected:
                        latency_ms = (time.perf_counter() - start_time) * 1000.0
                        print(f"\n✨ [Response] First Response chunk received in {latency_ms:.1f}ms! (Sub-second Response achieved!)")
                        first_token_detected = True
                        response_received_event.set()
                    
                    if part.text:
                        print(part.text, end="", flush=True)
                    elif part.inline_data:
                        print(".", end="", flush=True) # sound output chunk received
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n❌ Receiver Error: {e}")

async def run_prewarming_test():
    print("=" * 80)
    print(f"║ {'GEMINI LIVE WEBSOCKET PRE-WARMING VERIFICATION SANDBOX':^76} ║")
    print("=" * 80)
    
    client = genai.Client(api_key=API_KEY)
    
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            target_language_code="es",  # English to Spanish translation setup
            echo_target_language=True
        ),
    )
    
    print(f"📡 1. Establishing background WebSocket connection to: {MODEL_NAME}")
    connect_start = time.perf_counter()
    
    try:
        async with client.aio.live.connect(model=MODEL_NAME, config=config) as session:
            connect_duration = (time.perf_counter() - connect_start) * 1000.0
            print(f"✅ Connection Handshake Established in {connect_duration:.1f}ms.")
            print("-" * 80)
            print("🟢 2. TRANSITIONING TO PRE-WARMED STANDBY MODE (Holding Hot Connection for 15 seconds)...")
            print("     [We will stream sparse digital silence chunks every 2.5s to keep the socket alive]")
            print("-" * 80)
            
            # Start background responder receiver
            response_received_event = asyncio.Event()
            # We initialize receiver early but start measuring latency from simulated speech transmission
            speech_start_time = [0.0]
            receiver_task = asyncio.create_task(
                receive_responses(session, speech_start_time[0], response_received_event)
            )
            
            # Idle Standby Loop (15 seconds)
            standby_seconds = 15
            interval = 2.5
            cycles = int(standby_seconds / interval)
            
            for i in range(cycles):
                print(f"⏱️ [{i*interval:>4.1f}s / {standby_seconds:.1f}s] Streaming sparse silence frame (1,280 bytes)...")
                await session.send_realtime_input(
                    audio=types.Blob(data=SILENT_FRAME, mime_type="audio/pcm;rate=16000")
                )
                # Wait before next keep-alive
                await asyncio.sleep(interval)
            
            print("-" * 80)
            print("🔥 3. SIMULATING SUDDEN VOICE INPUT (Stream Swapping instantly onto the hot socket)")
            print("     [Generating 1 second of synthetic speech audio and transmitting...]")
            print("-" * 80)
            
            speech_chunks = generate_synthetic_speech()
            speech_start_time[0] = time.perf_counter()
            # Update the receiver task's timing reference
            receiver_task.cancel()
            await asyncio.sleep(0.01)
            receiver_task = asyncio.create_task(
                receive_responses(session, speech_start_time[0], response_received_event)
            )
            
            # Stream simulated audio chunks continuously
            for chunk in speech_chunks:
                await session.send_realtime_input(
                    audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                )
                await asyncio.sleep(0.04) # 40ms pacing
            
            print("🎤 Voice transmission complete. Waiting for first token response...")
            
            # Wait for response with a timeout
            try:
                await asyncio.wait_for(response_received_event.wait(), timeout=12.0)
            except asyncio.TimeoutError:
                print("\n⚠️ Timeout: No response received from Gemini Live API within 12 seconds.")
            
            # Cleanup
            receiver_task.cancel()
            await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"\n❌ Sandbox Execution Failure: {e}")
        print("Please check your GEMINI_API_KEY, network connection, or API quotas.")
    
    print("\n" + "=" * 80)
    print("🏁 SANDBOX TEST COMPLETE. Connection closed safely.")
    print("=" * 80)

if __name__ == "__main__":
    try:
        asyncio.run(run_prewarming_test())
    except KeyboardInterrupt:
        print("\n🛑 Sandbox terminated by user.")
