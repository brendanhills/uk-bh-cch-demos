# /// script
# dependencies = [
#     "websockets",
# ]
# ///

import asyncio
import json
import websockets
import sys

async def main():
    url = "ws://127.0.0.1:9000/ws"
    print(f"Connecting to WebSocket: {url}...")
    try:
        async with websockets.connect(url) as websocket:
            print("Connected! Sending start payload for Vietnamese paediatric scenario...")
            start_payload = {
                "action": "start",
                "preset": "vietnamese",
                "model": "gemini-3.1-flash-live-preview",
                "pacing": "auto",
                "pause": 15,
                "timeout": 15,
                "ceased_audio_threshold": 4.5,
                "startup_audio_threshold": 15,
                "additional_pause_sec": 2
            }
            await websocket.send(json.dumps(start_payload))
            print("Start payload sent. Listening to interpreter backend events in real-time...")
            print("=" * 80)

            while True:
                msg_str = await websocket.recv()
                msg = json.loads(msg_str)
                
                msg_type = msg.get("type")
                if msg_type == "status":
                    print(f"\n⭐ [STATUS] {msg.get('status')}")
                    if msg.get("status") == "completed":
                        print("Call completed successfully!")
                        break
                elif msg_type == "transcript_chunk":
                    speaker = msg.get("speaker")
                    direction = msg.get("direction", "unknown")
                    text = msg.get("text", "")
                    sys.stdout.write(f"[{speaker.upper()} chunk]: {text}\n")
                    sys.stdout.flush()
                elif msg_type == "turn_complete":
                    speaker = msg.get("speaker")
                    orig = msg.get("original", "")
                    trans = msg.get("translated", "")
                    print("\n" + "=" * 80)
                    print(f"🗣️  TURN COMPLETE: {speaker.upper()}")
                    print(f"   Original:   {orig}")
                    print(f"   Translated: {trans}")
                    print("=" * 80 + "\n")
                elif msg_type == "original_audio":
                    # Suppress original audio chunk logs
                    pass
                elif msg_type == "translated_audio":
                    # Suppress translated audio chunk logs
                    pass
                else:
                    print(f"🔹 [EVENT] {msg}")

    except KeyboardInterrupt:
        print("\nDisconnecting...")
    except Exception as e:
        print(f"❌ WebSocket error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
