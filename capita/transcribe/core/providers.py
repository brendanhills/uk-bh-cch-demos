import asyncio
import datetime
from .models import TranscriptionEvent
from google.cloud import speech_v2 as cs_v2
from google.cloud import speech_v1 as cs_v1

from google.api_core.client_options import ClientOptions

class V2Provider:
    """Wraps Google STT V2 API and yields TranscriptionEvents."""
    def __init__(self, client: cs_v2.SpeechAsyncClient, recognizer_name: str, model: str):
        self.client = client
        self.recognizer_name = recognizer_name
        self.model = model
        self.current_audio_time = 0.0
        
        # Determine location from recognizer_name for endpoint selection
        # format: projects/{p}/locations/{loc}/recognizers/{r}
        self.api_location = recognizer_name.split("/")[3]
        self.is_chirp = "chirp" in model.lower()

    async def _get_or_create_recognizer(self):
        """Fetches an existing V2 Recognizer or creates one."""
        try:
            return await self.client.get_recognizer(name=self.recognizer_name)
        except Exception:
            # Create recognizer if not found
            parent = "/".join(self.recognizer_name.split("/")[:4])
            recognizer_id = self.recognizer_name.split("/")[-1]
            
            features = cs_v2.RecognitionFeatures(
                enable_word_time_offsets=not self.is_chirp,
                enable_automatic_punctuation=True,
            )
            
            request = cs_v2.CreateRecognizerRequest(
                parent=parent,
                recognizer_id=recognizer_id,
                recognizer=cs_v2.Recognizer(
                    default_recognition_config=cs_v2.RecognitionConfig(
                        language_codes=["en-US"], 
                        model=self.model,
                        features=features,
                    ),
                ),
            )
            op = await self.client.create_recognizer(request=request)
            return await op.result()

    async def stream(self, audio_gen, channel_id=1, multi_channel=False, diarization=False, chunk_duration_sec=0.25):
        """Generates requests and yields events from the response stream."""
        # Ensure recognizer exists
        await self._get_or_create_recognizer()
        
        # 1. Config Request
        # Chirp 3 does not support word timestamps in streaming
        enable_word_offsets = not self.is_chirp

        features = cs_v2.RecognitionFeatures(
            enable_word_time_offsets=enable_word_offsets,
            enable_automatic_punctuation=True,
            multi_channel_mode=cs_v2.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if multi_channel else None
        )
        if diarization:
            features.diarization_config = cs_v2.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

        config = cs_v2.RecognitionConfig(
            features=features,
            explicit_decoding_config=cs_v2.ExplicitDecodingConfig(
                encoding=cs_v2.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                audio_channel_count=2 if multi_channel else 1,
            ),
            model=self.model,
            language_codes=["en-US"]
        )

        streaming_config = cs_v2.StreamingRecognitionConfig(
            config=config,
            streaming_features=cs_v2.StreamingRecognitionFeatures(
                interim_results=True,
                enable_voice_activity_events=True
            )
        )

        async def request_generator():
            yield cs_v2.StreamingRecognizeRequest(recognizer=self.recognizer_name, streaming_config=streaming_config)
            chunks_sent = 0
            async for chunk in audio_gen:
                chunks_sent += 1
                self.current_audio_time = chunks_sent * chunk_duration_sec
                yield cs_v2.StreamingRecognizeRequest(audio=chunk)

        responses = await self.client.streaming_recognize(requests=request_generator())
        
        async for response in responses:
            # Handle VAD
            if response.speech_event_type:
                ev_type = cs_v2.StreamingRecognizeResponse.SpeechEventType(response.speech_event_type).name
                yield TranscriptionEvent(
                    speaker_id=channel_id, text="", 
                    start_sec=self.current_audio_time, end_sec=self.current_audio_time,
                    is_final=True, event_type=ev_type.lower()
                )

            # Handle Results
            for result in response.results:
                if not result.alternatives: continue
                alt = result.alternatives[0]
                
                # Attribution
                speaker = channel_id
                if multi_channel: speaker = result.channel_tag
                if diarization and alt.words: speaker = alt.words[0].speaker_tag

                # Timing
                start = alt.words[0].start_offset.total_seconds() if alt.words else self.current_audio_time
                end = alt.words[-1].end_offset.total_seconds() if alt.words else (start + 1.0)

                yield TranscriptionEvent(
                    speaker_id=speaker,
                    text=alt.transcript,
                    start_sec=start,
                    end_sec=end,
                    is_final=result.is_final,
                    words=[{"word": w.word, "start": w.start_offset.total_seconds()} for w in alt.words]
                )

class V1Provider:
    """Wraps Google STT V1 API (for Mono Diarization)."""
    def __init__(self, client: cs_v1.SpeechAsyncClient):
        self.client = client
        self.current_audio_time = 0.0
        self.speaker_history = {} # {speaker_id: [(timestamp, text)]}

    def _should_yield_chunk(self, speaker_id, start_sec, text):
        """
        V1 Diarization often 'corrects' itself by re-sending chunks.
        Uses fuzzy matching to detect duplicates and extensions.
        Returns (should_yield, modified_text, is_final)
        """
        text = text.strip()
        if not text: return False, text, False
        
        if speaker_id not in self.speaker_history:
            self.speaker_history[speaker_id] = []
        history = self.speaker_history[speaker_id]
        
        # 1. Deduplication / Extension Check
        import difflib
        for i in range(len(history) - 1, max(-1, len(history) - 5), -1):
            prev_ts, prev_text = history[i]
            if abs(start_sec - prev_ts) < 1.0:
                if prev_text.startswith(text): return False, text, False
                if text.startswith(prev_text):
                    # It's an extension of the same thought
                    new_part = text[len(prev_text):].strip()
                    if not new_part: return False, text, False
                    history[i] = (start_sec, text)
                    return True, new_part, True # Yield only the new part
                
                # It's a correction
                history[i] = (start_sec, text)
                return True, text, True

        history.append((start_sec, text))
        return True, text, True

    async def stream(self, audio_gen):
        config = cs_v1.RecognitionConfig(
            encoding=cs_v1.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US",
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
            diarization_config=cs_v1.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2, max_speaker_count=2,
            ),
            model="phone_call", use_enhanced=True,
        )
        
        streaming_config = cs_v1.StreamingRecognitionConfig(config=config, interim_results=True)

        # We must use a queue or similar to interleave heartbeats with request generation
        # or simply yield heartbeats directly from the main stream loop
        
        async def request_generator():
            yield cs_v1.StreamingRecognizeRequest(streaming_config=streaming_config)
            chunks_sent = 0
            async for chunk in audio_gen:
                chunks_sent += 1
                self.current_audio_time = chunks_sent * 0.25
                yield cs_v1.StreamingRecognizeRequest(audio_content=chunk)

        # Yield an initial "Connecting" signal
        yield TranscriptionEvent(speaker_id=1, text="", start_sec=0.0, end_sec=0.0, is_final=False, event_type="heartbeat")

        responses = await self.client.streaming_recognize(requests=request_generator())
        
        async for response in responses:
            if not response.results: continue
            result = response.results[0]
            if not result.alternatives: continue
            alt = result.alternatives[0]

            if result.is_final:
                if alt.words:
                    # Group words by speaker to create turns immediately
                    current_speaker = alt.words[0].speaker_tag
                    current_text = []
                    current_start = alt.words[0].start_time.total_seconds()
                    
                    for word in alt.words:
                        if word.speaker_tag != current_speaker:
                            # Speaker changed, yield the previous turn
                            yield TranscriptionEvent(
                                speaker_id=current_speaker,
                                text=" ".join(current_text),
                                start_sec=current_start,
                                end_sec=word.start_time.total_seconds(),
                                is_final=True
                            )
                            current_speaker = word.speaker_tag
                            current_text = [word.word]
                            current_start = word.start_time.total_seconds()
                        else:
                            current_text.append(word.word)
                    
                    # Yield the last remaining turn
                    if current_text:
                        yield TranscriptionEvent(
                            speaker_id=current_speaker,
                            text=" ".join(current_text),
                            start_sec=current_start,
                            end_sec=alt.words[-1].end_time.total_seconds(),
                            is_final=True
                        )
                else:
                    # Fallback for result without words
                    yield TranscriptionEvent(
                        speaker_id=1, text=alt.transcript,
                        start_sec=self.current_audio_time - 1.0, 
                        end_sec=self.current_audio_time,
                        is_final=True
                    )
            else:
                # Interim
                if alt.transcript.strip():
                    yield TranscriptionEvent(
                        speaker_id=1, 
                        text=alt.transcript,
                        start_sec=self.current_audio_time,
                        end_sec=self.current_audio_time,
                        is_final=False
                    )
