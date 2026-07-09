# Plan: Programmatic Simultaneous Sample Generation (`simultaneous_samples`)

## Phase 1: Dialogue Script Library Setup (JSON Metadata)
- [ ] **Task 1.1**: Set up directory structure for sample metadata
  *   Create directory `samples/metadata/` if it does not exist.
- [ ] **Task 1.2**: Re-use and port pre-existing dialogue script files into JSON metadata
  *   Locate pre-existing dialogue scenarios inside current generation scripts (e.g. `generate_bilingual_audio.py`, `generate_german_audio.py`, etc.).
  *   Extract and port their exact spoken turns and texts to prevent redundant dialogue writing.
  *   Write [de_fever_session.json](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/HealthDirect/samples/metadata/de_fever_session.json) for the German Headache & Fever Scenario.
  *   Write [es_ear_session.json](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/HealthDirect/samples/metadata/es_ear_session.json) for the Spanish Ear Infection Scenario.
  *   Write [vi_fever_session.json](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/HealthDirect/samples/metadata/vi_fever_session.json) for the Vietnamese Child Paediatric Consultation.
  *   *Verification*: Ensure every turn defines `speaker`, `text`, `lang_code`, `voice_name`, and `gender` (mapped to Text-to-Speech SsmlVoiceGender values).

## Phase 2: Synthesis Pipeline Development (`generate_simultaneous_audio.py`)
- [ ] **Task 2.1**: Initialize the base script and dependencies
  *   Create the script file [generate_simultaneous_audio.py](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/HealthDirect/generate_simultaneous_audio.py).
  *   Configure imports: `asyncio`, `os`, `io`, `pydub`, `google.cloud.texttospeech`, `google.cloud.storage`.
  *   Bypass mTLS to prevent OpenSSL Context mutation bugs on Google corp systems:
      ```python
      os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
      os.environ["GOOGLE_API_USE_MTLS"] = "never"
      ```
- [ ] **Task 2.2**: Implement Asynchronous Voice Synthesizer with Emotional SSML Gearing
  *   Write `async def synthesize_voice(text, language_code, voice_name, gender) -> AudioSegment`.
  *   For Patient turns, programmatically wrap the text in SSML tags:
      *   Apply `<prosody rate="85%" pitch="-2st">` to slow the speech and lower pitch, mimicking a weary, sick speaker.
      *   Inject `<break time="500ms"/>` between clauses to simulate heavy breathing and painful pauses.
      *   Apply `<emphasis level="moderate">` on key symptoms like pain, headache, and fever.
  *   Make calls using `TextToSpeechAsyncClient.synthesize_speech()` requesting `LINEAR16` audio at `16000Hz`.
  *   Ingest raw synthesized bytes into `pydub.AudioSegment`.
- [ ] **Task 2.3**: Implement the Simultaneous Timeline Compiler
  *   Write `async def compile_simultaneous_stereo_wav(scenario_id, script, tail_buffer_ms=2500)`.
  *   Initialize silent mono `left_channel` and `right_channel` canvases.
  *   Iterate through the script, keeping a running `current_time_ms`.
  *   Synthesize turn audio, overlay it on the correct channel canvas at `current_time_ms`, and increment the playhead by `len(audio) + tail_buffer_ms`.
  *   Merge canvases using `AudioSegment.from_mono_audiosegments(left_channel, right_channel)`.
- [ ] **Task 2.4**: Implement GCS Upload Integration
  *   Write `def upload_to_gcs(audio_segment, bucket_name, gcs_path)`.
  *   Export audio to a memory buffer (`io.BytesIO`) as a WAV file, and upload to `gs://uk-bh-experiments-argolis-us/HealthDirect/call_samples/`.
  *   Add error handling to skip GCS upload gracefully if credentials are not configured locally.

## Phase 3: Compilation and Verification
- [ ] **Task 3.1**: Run compilation pipeline
  *   Execute `python generate_simultaneous_audio.py` to synthesize all 3 scenarios.
  *   *Verification*: Confirm that `de_fever_session.wav`, `es_ear_session.wav`, and `vi_fever_session.wav` are generated under `samples/`.
- [ ] **Task 3.2**: Audio Channel & Timing Verification
  *   Check that the generated files have correct Left/Right speaker separation (Patient in Left ear, Nurse in Right ear).
  *   Verify that the silence gap between the end of a spoken turn on one channel and the start of a turn on the other channel measures exactly `2.5 seconds`.
  *   Ensure there are no overlapping voices *within* the pre-recorded files themselves (the files should be paced perfectly for simultaneous translation, where the translation itself will fill the silence gaps on the other channel).
- [ ] **Task 3.3**: GCS Verification
  *   Ensure files are successfully pushed to Google Cloud Storage under `gs://uk-bh-experiments-argolis-us/HealthDirect/call_samples/`.
