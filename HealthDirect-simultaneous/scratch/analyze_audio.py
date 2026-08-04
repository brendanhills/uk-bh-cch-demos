import os
import array
from pydub import AudioSegment

def has_speech(chunk: bytes, threshold: int = 1000) -> bool:
    if not chunk:
        return False
    if len(chunk) % 2 != 0:
        chunk = chunk[:len(chunk) - 1]
    samples = array.array('h', chunk)
    return any(abs(s) > threshold for s in samples)

def analyze():
    file_path = 'samples/paediatric_vietnamese_demo.wav'
    seg = AudioSegment.from_file(file_path).set_frame_rate(16000).set_sample_width(2)
    left_mono = seg.split_to_mono()[0]
    right_mono = seg.split_to_mono()[1]
    
    patient_bytes = left_mono.raw_data
    nurse_bytes = right_mono.raw_data
    
    chunk_size = 3200  # 100ms
    max_len = max(len(patient_bytes), len(nurse_bytes))
    
    current_speaker = None
    speech_start = 0
    
    print("Timeline analysis (threshold = 1000, 100ms chunks):")
    print("-" * 50)
    
    for i in range(0, max_len, chunk_size):
        time_sec = (i / chunk_size) * 0.1
        chunk_p = patient_bytes[i:i+chunk_size]
        chunk_n = nurse_bytes[i:i+chunk_size]
        
        p_has = has_speech(chunk_p)
        n_has = has_speech(chunk_n)
        
        detected_speaker = None
        if p_has and n_has:
            detected_speaker = "both"
        elif p_has:
            detected_speaker = "patient"
        elif n_has:
            detected_speaker = "nurse"
        else:
            detected_speaker = "silence"
            
        if detected_speaker != current_speaker:
            if current_speaker is not None:
                print(f"[{speech_start:.1f}s - {time_sec:.1f}s] {current_speaker}")
            current_speaker = detected_speaker
            speech_start = time_sec
            
    print(f"[{speech_start:.1f}s - {(max_len/chunk_size)*0.1:.1f}s] {current_speaker}")

if __name__ == '__main__':
    analyze()
