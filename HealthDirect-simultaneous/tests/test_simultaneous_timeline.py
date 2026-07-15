import os
import json
import wave
import pytest
from pydub import AudioSegment

METADATA_FILES = [
    ("german",
     "samples/scripts/de_fever_session.json",
     "samples/de_fever_session.wav"),
    ("spanish",
     "samples/scripts/es_ear_session.json",
     "samples/es_ear_session.wav"),
    ("vietnamese",
     "samples/scripts/vi_paediatric_session.json",
     "samples/vi_paediatric_session.wav"),
    ("arabic",
     "samples/scripts/ar_asthma_session.json",
     "samples/ar_asthma_session.wav"),
    ("hindi",
     "samples/scripts/hi_cough_session.json",
     "samples/hi_cough_session.wav")
]


@pytest.mark.parametrize("preset,meta_path,wav_path", METADATA_FILES)
def test_simultaneous_audio_timeline_and_isolation(preset, meta_path, wav_path):
    """Physical timeline analyzer test.

    Loads compiled WAVs, splits them into mono channels, and programmatically
    verifies channel isolation, overlap limits, and pacing buffers.
    """
    # Skip if WAV hasn't been generated
    if not os.path.exists(wav_path) or not os.path.exists(meta_path):
        pytest.skip(
            f"Compiled file or metadata missing for {preset}. "
            f"Run generate_simultaneous_audio.py first."
        )
        
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    turns = meta_data["turns"]
    
    # Load stereo WAV and split into mono Left/Right channels
    stereo_audio = AudioSegment.from_wav(wav_path)
    assert stereo_audio.channels == 2, (
        f"Compiled audio for {preset} is not stereo (dual channel)!"
    )
    
    left_channel, right_channel = stereo_audio.split_to_mono()
    
    print(f"\n--- Checking Audio Timeline: {preset.upper()} ({wav_path}) ---")
    
    # Analyze speaker segments
    for idx, turn in enumerate(turns):
        speaker = turn["speaker"]
        start_ms = turn["start_ms"]
        
        # We check the RMS of a 2-second sub-segment after the turn start
        segment_duration_ms = 2000
        
        left_slice = left_channel[start_ms : start_ms + segment_duration_ms]
        right_slice = right_channel[start_ms : start_ms + segment_duration_ms]
        
        print(f"  Turn {idx+1} ({speaker.upper()} "
              f"starts at {start_ms/1000:.2f}s): "
              f"Left RMS={left_slice.rms}, Right RMS={right_slice.rms}")
        
        # Silence threshold: quiet channels have RMS < 10, speech have RMS > 100
        if speaker in ["caller", "patient"]:
            # Caller is in Left ear: Left high energy, Right silence
            assert left_slice.rms > 100, (
                f"Left channel is silent when patient should be speaking "
                f"on Turn {idx+1}!"
            )
            assert right_slice.rms < 10, (
                f"Cross-talk detected! Right channel has vocal energy "
                f"on Turn {idx+1} (RMS={right_slice.rms})!"
            )
        else:
            # Nurse is in Right ear: Right high energy, Left silence
            assert right_slice.rms > 100, (
                f"Right channel is silent when nurse should be speaking "
                f"on Turn {idx+1}!"
            )
            assert left_slice.rms < 10, (
                f"Cross-talk detected! Left channel has vocal energy "
                f"on Turn {idx+1} (RMS={left_slice.rms})!"
            )


def test_timeline_spacing_accuracy():
    """Verifies silence gaps between turns inside metadata and physical wave.

    Ensures pacing bounds are strictly met.
    """
    for preset, meta_path, wav_path in METADATA_FILES:
        if not os.path.exists(meta_path) or not os.path.exists(wav_path):
            continue
            
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        turns = data["turns"]
        stereo_audio = AudioSegment.from_wav(wav_path)
        left_channel, right_channel = stereo_audio.split_to_mono()
        
        for idx in range(1, len(turns)):
            prev_turn = turns[idx-1]
            curr_turn = turns[idx]
            
            time_difference = curr_turn["start_ms"] - prev_turn["start_ms"]
            
            # Slices active channel to measure its non-silent length
            is_caller = prev_turn["speaker"] in ["caller", "patient"]
            active_channel = left_channel if is_caller else right_channel
            
            # Find actual duration by stripping silence at the end
            non_silent_ms = 0
            # Step in 50ms increments backwards to find where speech ended
            for offset in range(time_difference, 0, -50):
                target_start = prev_turn["start_ms"] + offset - 50
                target_end = prev_turn["start_ms"] + offset
                sub_slice = active_channel[target_start:target_end]
                if sub_slice.rms > 50:
                    non_silent_ms = offset
                    break
                    
            # Assert the strict chronological scheduling logic in metadata
            assert curr_turn["start_ms"] >= prev_turn["start_ms"] + 2500, (
                f"Scheduling overlap! Turn {idx+1} starts too early: "
                f"{curr_turn['start_ms']}ms."
            )
            
            actual_gap_ms = time_difference - non_silent_ms
            print(f"[{preset.upper()}] Gap {idx} to {idx+1}: {actual_gap_ms}ms")
            
            # Assert physical silence gap is within our 2500ms pacing tolerance
            assert 2300 <= actual_gap_ms <= 3600, (
                f"Timeline spacing failure for {preset}! Gap between "
                f"Turn {idx} and {idx+1} measures {actual_gap_ms}ms "
                f"instead of 2500ms."
            )
