"""
Utility functions for orchestrating the transcription pipeline.
Provides common argument parsing, pipeline setup, and audio broadcasting logic.
"""

import argparse
import os
import asyncio
import audioop
import logging
from pathlib import Path
from dotenv import load_dotenv
from .engine import TranscriptionEngine
from .sinks import TerminalSink, RealTimeJsonSink
from simulate_audio import AudioStreamSimulator

def parse_common_args(description: str, is_mono: bool = False, is_parallel: bool = False):
    """
    Standard argument parser for all transcription demo scripts.
    
    Args:
        description: The help text for the CLI.
        is_mono: If True, hides stereo-specific flags like '--mode'.
        is_parallel: If True, shows architecture-specific flags like '--arch'.
    """
    load_dotenv()
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("gcs_uri", help="Path to audio file (Local path or gs:// URI)")
    parser.add_argument("--model", default="telephony", help="STT model (e.g., telephony, chirp) [Default: telephony]")
    parser.add_argument("--stability", type=float, help="Seconds to buffer results for chronological sorting [Default: 1.0]")
    parser.add_argument("--gap", type=float, help="Seconds of silence between words to trigger a turn split [Default: 0.5]")
    parser.add_argument("--sample-rate", type=int, default=16000, help="Target sample rate in Hz [Default: 16000]")
    parser.add_argument("--chunk-size", type=float, default=0.1, help="Audio chunk duration in seconds [Default: 0.1]")
    parser.add_argument("--wait-for-play", action="store_true", help="Wait for user to start audio playback in browser")
    parser.add_argument("--duration", type=float, default=None, help="Stop after X seconds of audio")
    parser.add_argument("--sensitivity", choices=["STANDARD", "SHORT", "SUPERSHORT"], default="STANDARD",
                        help="Endpointing sensitivity for Chirp-3 models [Default: STANDARD]")
    parser.add_argument("--start-timeout", type=float, default=0.5,
                        help="Speech start timeout in seconds [Default: 0.5]")
    
    if not is_mono:
        parser.add_argument("--mode", choices=["low_latency", "readability"], default="readability",
                            help="readability (buffered/stable) vs low_latency (instant/unstable) [Default: readability]")
    
    if is_parallel:
        parser.add_argument("--arch", choices=["mode_a", "mode_b"], default="mode_a",
                            help="mode_a (Centralized Interleaving) vs mode_b (Distributed Stabilization) [Default: mode_a]")
    
    return parser.parse_args()

async def setup_pipeline(args, approach_name: str, force_mono: bool = False):
    """
    Initializes the core components (Simulator, Engine, Sinks) based on CLI arguments.
    
    Returns:
        tuple: (simulator, engine, terminal_sink, json_sink, output_path)
    """
    # 1. Prepare Audio Source
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=force_mono, target_sample_rate=args.sample_rate)
    await simulator.prepare()
    
    # Generate signed URL for optional browser playback (helpful for remote VMs)
    if args.gcs_uri.startswith("gs://"):
        simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()
    
    # 2. Configure the Engine
    engine = TranscriptionEngine()
    
    # Adaptive Stability: High-latency models (Chirp) need a larger buffer for sorting
    if "chirp" in args.model.lower():
        engine.STABILITY_THRESHOLD = 5.0
    
    mode = getattr(args, 'mode', 'readability')
    arch = getattr(args, 'arch', 'mode_a')
    
    if mode == "low_latency" or arch == "mode_b":
        # In Mode B, the workers handle stabilization and gap-splitting.
        # The engine should just pass events through (interleaving still happens if they arrive simultaneously).
        engine.STABILITY_THRESHOLD = 0.0
        engine.GAP_THRESHOLD = 0.0
        engine.ACTIVE_BLOCKING = False
    
    # Apply manual overrides if provided
    if args.stability is not None:
        engine.STABILITY_THRESHOLD = args.stability
    if args.gap is not None:
        engine.GAP_THRESHOLD = args.gap

    # 3. Setup UI and Logging Sinks
    terminal = TerminalSink()
    
    # Generate a descriptive filename for the output
    audio_filename = Path(args.gcs_uri).name
    blocking_tag = "b1" if engine.ACTIVE_BLOCKING else "b0"
    arch_tag = arch
    params_str = f"{args.model}_{arch_tag}_s{engine.STABILITY_THRESHOLD}_g{engine.GAP_THRESHOLD}_{blocking_tag}_{args.sample_rate}hz"
    output_path = f"output/{audio_filename}_{approach_name}_{params_str}.json"
    
    json_log = RealTimeJsonSink(output_path)
    json_log.open()
    
    # Connect sinks to the engine
    engine.add_sink(terminal.emit)
    engine.add_sink(json_log.emit)
    
    return simulator, engine, terminal, json_log, output_path

async def run_broadcaster(simulator, engine, audio_queues, duration, chunk_size, broadcast_stereo=False):
    """
    The 'Heartbeat' of the system. Streams audio from the simulator and
    distributes it to one or more worker queues while driving the engine clock.
    """
    chunks_sent = 0
    async for chunk in simulator.stream(duration=duration, chunk_duration_sec=chunk_size):
        chunks_sent += 1
        
        # Advance the engine's internal playhead based on audio time
        engine.set_audio_time(chunks_sent * chunk_size)
        
        if isinstance(audio_queues, list):
            if broadcast_stereo:
                # Comparison Mode: Send same stereo chunk to all workers
                for q in audio_queues:
                    await q.put(chunk)
            else:
                # Parallel Mode: Split stereo into two mono chunks for independent workers
                # audio_queues[0] gets Left (Caller), audio_queues[1] gets Right (Agent)
                await audio_queues[0].put(audioop.tomono(chunk, 2, 1, 0))
                await audio_queues[1].put(audioop.tomono(chunk, 2, 0, 1))
        else:
            # Two-Channel Mode: Send raw stereo chunk to a single worker
            await audio_queues.put(chunk)
            
    # Signal EOF to workers
    if isinstance(audio_queues, list):
        for q in audio_queues: await q.put(None)
    else:
        await audio_queues.put(None)

async def q_gen(q):
    """Simple adapter to convert an asyncio.Queue into an async generator."""
    while True:
        chunk = await q.get()
        if chunk is None: 
            break
        yield chunk
