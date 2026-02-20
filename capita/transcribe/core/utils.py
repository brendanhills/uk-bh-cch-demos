import argparse
import os
import asyncio
from dotenv import load_dotenv
from .engine import TranscriptionEngine
from .sinks import TerminalSink, RealTimeJsonSink
from simulate_audio import AudioStreamSimulator

def parse_common_args(description: str, is_mono: bool = False):
    """Common argument parser for all transcription demos."""
    load_dotenv()
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("gcs_uri", help="Path to audio file (Local or GS)")
    parser.add_argument("--model", default="telephony")
    parser.add_argument("--stability", type=float, help="Stability threshold override (seconds)")
    parser.add_argument("--gap", type=float, help="Gap threshold override (seconds)")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Target sample rate (Hz)")
    parser.add_argument("--chunk-size", type=float, default=0.1, help="Audio chunk duration (seconds)")
    parser.add_argument("--wait-for-play", action="store_true", help="Pause for user to start audio.")
    parser.add_argument("--duration", type=float, default=None)
    
    if not is_mono:
        parser.add_argument("--mode", choices=["low_latency", "readability"], default="readability")
    
    return parser.parse_args()

async def setup_pipeline(args, approach_name: str, force_mono: bool = False):
    """Common pipeline setup for engine, sinks, and simulator."""
    # 1. Prepare Audio Source
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=force_mono, target_sample_rate=args.sample_rate)
    await simulator.prepare()
    
    # Generate signed URL for browser playback (since VM speakers often don't work)
    if args.gcs_uri.startswith("gs://"):
        simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()
    
    # 2. Setup Engine
    engine = TranscriptionEngine()
    mode = getattr(args, 'mode', 'readability')
    if mode == "low_latency":
        engine.STABILITY_THRESHOLD = 0.0
        engine.ACTIVE_BLOCKING = False
    
    # Manual overrides
    if args.stability is not None:
        engine.STABILITY_THRESHOLD = args.stability
    if args.gap is not None:
        engine.GAP_THRESHOLD = args.gap

    # 3. Setup Sinks
    terminal = TerminalSink()
    
    audio_base = os.path.basename(args.gcs_uri)
    params_str = f"m={args.model}_s={engine.STABILITY_THRESHOLD}_g={engine.GAP_THRESHOLD}_r={args.sample_rate}_c={args.chunk_size}"
    output_path = f"output/{audio_base}_{approach_name}_{params_str}.json"
    
    json_log = RealTimeJsonSink(output_path)
    json_log.open()
    
    engine.add_sink(terminal.emit)
    engine.add_sink(json_log.emit)
    
    return simulator, engine, terminal, json_log, output_path

async def run_broadcaster(simulator, engine, audio_queues, duration, chunk_size):
    """Generic broadcaster that drives the engine clock and distributes audio."""
    import audioop
    chunks_sent = 0
    async for chunk in simulator.stream(duration=duration, chunk_duration_sec=chunk_size):
        chunks_sent += 1
        engine.set_audio_time(chunks_sent * chunk_size)
        
        # Audio_queues can be a single queue or a list of queues
        if isinstance(audio_queues, list):
            # Split stereo into mono for each queue
            # Assuming 2 queues for parallel
            await audio_queues[0].put(audioop.tomono(chunk, 2, 1, 0))
            await audio_queues[1].put(audioop.tomono(chunk, 2, 0, 1))
        else:
            await audio_queues.put(chunk)
            
    if isinstance(audio_queues, list):
        for q in audio_queues: await q.put(None)
    else:
        await audio_queues.put(None)

async def q_gen(q):
    """Helper to convert a queue into a generator."""
    while True:
        chunk = await q.get()
        if chunk is None: break
        yield chunk
