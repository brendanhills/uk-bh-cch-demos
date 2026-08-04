# Specification: Programmatic Simultaneous Sample Generation (`simultaneous_samples`)

## 1. Overview
Develop an automated, programmatic pipeline to synthesize bilingual conversational sample audio files that are optimized for **simultaneous translation and interpretation** testing. 

These sample tracks are dual-channel stereo WAV files (Left Channel: Patient Native language, Right Channel: Clinician English). By incorporating highly precise, mathematically calculated **overlap timing gaps (simultaneous pacing)**, the generated files can be streamed continuously at 100% real-time speed. This eliminates all server-side socket-pausing state machines while ensuring translated text and audio play back naturally inside the pre-synthesized conversational pauses on the client browsers.

---

## 2. Functional Requirements

### 2.1 Pacing & Timeline Algorithm (Simultaneous Overlap)
- **Concept**: Since Gemini Live translates in real-time as a person speaks, translation audio starts playing *before* the speaker finishes. The required silence gap *after* a speech turn ends is only needed for the "trailing tail" of the translation to complete.
- **Pacing Math**:
  Let $T_i$ be the $i$-th speech turn in a dialogue script. Each turn has:
  *   $S_i$: Physical start time in milliseconds.
  *   $D_i$: Duration of synthesized speech in milliseconds (obtained from the synthesized audio segment length).
  *   $E_i = S_i + D_i$: Physical end time of speech.
  *   $P_i$: Overlapped playback latency buffer. Since translation playback is concurrent, the estimated translation playback duration $L_i$ overlaps with speech. We define the trailing tail buffer $\Delta \approx 2500\text{ms}$ (representing Gemini Live API round-trip network latency plus the final syllable translation tail).
  
  The start time of the next turn $T_{i+1}$ is scheduled as:
  $$S_{i+1} = E_i + \Delta = S_i + D_i + 2500\text{ms}$$
  
- **Silence Gaps**: The physical silence padding on a channel after a speaker finishes speaking is exactly $\Delta = 2500\text{ms}$. This compressed padding keeps the conversation extremely tight, rapid, and realistic.

### 2.2 Programmatic Synthesis Script (`generate_simultaneous_audio.py`)
- **Google Cloud Text-to-Speech (TTS) Integration**: 
  - Leverage `google-cloud-text-to-speech` asynchronous client (`TextToSpeechAsyncClient`).
  - Request audio in high-fidelity `LINEAR16` (PCM WAV) format with a target sample rate of `16000Hz` (16kHz).
- **Subtle Emotional Patient Voices (SSML Nuances)**:
  - To ensure the demo feels realistic and empathetic, **the Patient/Caller voice must convey a subtle level of worry, sickness, or distress** (since they or their child are unwell).
  - Since Google Cloud TTS standard voices are neutral, we will use **SSML (Speech Synthesis Markup Language)** tags programmatically inside the JSON turns:
    - **Prosody Control**: Use `<prosody rate="85%" pitch="-2st">` to speak slightly slower and at a lower pitch to reflect fatigue, exhaustion, or weakness.
    - **Emphasis**: Use `<emphasis level="moderate">` to emphasize symptoms (e.g. *headache*, *fever*, *pain*, *schmerzen*).
    - **Natural Pauses (Breaths)**: Insert precise pauses using `<break time="400ms"/>` or `<break time="800ms"/>` to simulate short hesitations, heavy breathing, or sighing due to physical discomfort.
  - **High-Fidelity Voice Selections**: Prioritize using premium `Neural2` or `Wavenet` voices for Patient targets, which offer the highest semantic realism and natural breathing structures.
- **Audio Canvas Manipulation**:
  - Initialize two high-resolution silent mono tracks of identical length using `pydub.AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)`.
  - Iterate through the dialogue script. Synthesize each turn.
  - If `turn["speaker"] == "patient"`: Overlay the synthesized SSML-wrapped audio onto the **Left Channel** canvas at `current_time_ms`.
  - If `turn["speaker"] == "nurse"`: Overlay the synthesized audio (standard, professional, calm clinician tone) onto the **Right Channel** canvas at `current_time_ms`.
  - Increment `current_time_ms` by $D_i + \Delta$ (duration of speech + 2.5s tail buffer).
- **Stereo Merging**:
  - Merge the Left (Patient) and Right (Nurse) mono canvases into a single dual-channel stereo track using `AudioSegment.from_mono_audiosegments(left_channel, right_channel)`.
  - Export the merged file as a standard PCM WAV locally to `samples/[scenario_id].wav`.

### 2.3 GCS Storage Upload Module
- Integrates with `google-cloud-storage` to back up the compiled stereo `.wav` file to GCS:
  - Bucket: `uk-bh-experiments-argolis-us`
  - GCS Target Directory: `HealthDirect/call_samples/`
  - Content Type: `audio/wav`
  - Implement graceful failure logic so that the script runs fine locally even if GCS credentials are not present.

---

## 3. Dialogue Scenario Scripts & Presets (Reusing Existing Scripts)

The pipeline will **re-use the exact text, speakers, and turns from the pre-existing generation scripts** inside the codebase (such as `generate_bilingual_audio.py`, `generate_german_audio.py`, etc.) to prevent redundant work and preserve scenario consistency. 

We will port these existing scripts into structured JSON metadata files under `samples/metadata/`. Each scenario must utilize premium voices appropriate for the language, gender, and age, fully enriched with subtle SSML emotion marks:

### 3.1 Scenario 1: German Fever & Headache (`de_fever_session`)
- **Patient Language**: German (`de-DE`)
- **Patient Voice**: `de-DE-Wavenet-B` (Male, SsmlVoiceGender.MALE)
- **Nurse Language**: Australian English (`en-AU`)
- **Nurse Voice**: `en-AU-Wavenet-C` (Female, SsmlVoiceGender.FEMALE)
- **Dialogue Flow**:
  1. Patient (German): "Good day. I am calling because I have had a very bad headache and some fever since this morning." (Est. 5.5s)
  2. Nurse (English): "Hello, thank you for calling HealthDirect. I am sorry to hear that. Do you have any neck stiffness or sensitivity to bright light?" (Est. 6.5s)
  3. Patient (German): "No, my neck feels normal, but bright light does indeed hurt my eyes a bit." (Est. 5.0s)
  4. Nurse (English): "I understand. Sensitivity to light can sometimes indicate a more serious issue. I recommend resting in a dark room and checking your temperature. If it goes above thirty-nine, please visit the clinic." (Est. 10.0s)
  5. Patient (German): "Thank you for the advice. I will measure my temperature immediately and lie down in a dark room." (Est. 5.0s)
  6. Nurse (English): "You are very welcome. Take care, and please call us back if your symptoms worsen." (Est. 4.5s)

### 3.2 Scenario 2: Spanish Ear Infection (`es_ear_session`)
- **Patient Language**: Spanish (`es-ES`)
- **Patient Voice**: `es-ES-Wavenet-C` (Female, SsmlVoiceGender.FEMALE)
- **Nurse Language**: Australian English (`en-AU`)
- **Nurse Voice**: `en-AU-Wavenet-B` (Male, SsmlVoiceGender.MALE)

### 3.3 Scenario 3: Vietnamese Child Paediatric Consultation (`vi_fever_session`)
- **Patient Language**: Vietnamese (`vi-VN`)
- **Patient Voice**: `vi-VN-Wavenet-A` (Female, SsmlVoiceGender.FEMALE)
- **Nurse Language**: Australian English (`en-AU`)
- **Nurse Voice**: `en-AU-Wavenet-C` (Female, SsmlVoiceGender.FEMALE)

---

## 4. Non-Functional Requirements
- **Audio Fidelity**: High-quality `16kHz`, 16-bit PCM Linear WAV. No clipping, compression artifacts, or dynamic drift.
- **Synthesizer Performance**: Script execution should leverage concurrent asynchronous coroutines (`asyncio.gather`) to synthesize turns in parallel, keeping compilation time under 15 seconds per file.

---

## 5. Acceptance Criteria
- [ ] **Dialogue Integrity**: The JSON script files are validated and parsed correctly.
- [ ] **Stereo Separation**: Spoken Patient words are heard *exclusively* in the Left ear, and spoken Nurse words *exclusively* in the Right ear.
- [ ] **Simultaneous Pacing Verification**: Silence gaps after speech segments measure exactly $2500\text{ms} \pm 100\text{ms}$.
- [ ] **Continuous Stream Output**: Playback of the compiled `.wav` file from start to finish flows naturally without awkward, prolonged dead-silence zones.
- [ ] **Robust Local & Cloud Backup**: Sells the compiled WAV locally and successfully uploads to the specified Google Cloud Storage bucket.
