"""
API Providers for Google Speech-to-Text (STT) V1 and V2.
These classes wrap the low-level GRPC streaming logic and yield standardized TranscriptionEvents.
"""

import asyncio
from google.cloud import speech_v2 as cs_v2
from google.cloud import speech_v1 as cs_v1
from .models import TranscriptionEvent

class V2Provider:
    """
    Unified wrapper for Google STT V2.
    Handles both standard models (telephony) and specialized ones (Chirp-3).
    """
    def __init__(self, client: cs_v2.SpeechAsyncClient, recognizer_name: str, model: str, endpoint_sensitivity: str = "STANDARD"):
        self.client = client
        self.recognizer_name = recognizer_name
        self.model = model
        self.current_audio_time = 0.0
        
        # Profile detection
        self.is_chirp = "chirp" in model.lower()

        # Map sensitivity to speech_end_timeout durations (demo-optimized)
        self.sensitivity_map = {
            "STANDARD": 3.0,
            "SHORT": 1.5,
            "SUPERSHORT": 0.5,
        }
        self.speech_end_timeout_sec = self.sensitivity_map.get(endpoint_sensitivity.upper(), 3.0)
        self.speech_start_timeout_sec = 0.5 # Demo optimized

    async def _get_or_create_recognizer(self):
        """Ensures the recognizer exists in the specified location."""
        try:
            await self.client.get_recognizer(name=self.recognizer_name)
        except Exception:
            # Create it if it doesn't exist
            parent = "/".join(self.recognizer_name.split("/")[:4])
            recognizer_id = self.recognizer_name.split("/")[-1]
            
            # Basic configuration for the recognizer
            # (Features can be overridden in the recognition config)
            features = cs_v2.RecognitionFeatures(
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
            )
            
            request = cs_v2.CreateRecognizerRequest(
                parent=parent,
                recognizer_id=recognizer_id,
                recognizer=cs_v2.Recognizer(
                    display_name=f"Demo Recognizer {recognizer_id}",
                    model=self.model,
                    default_recognition_config=cs_v2.RecognitionConfig(
                        features=features,
                        language_codes=["en-US"],
                    )
                )
            )
            operation = await self.client.create_recognizer(request=request)
            await operation.result()

    async def stream(self, audio_gen, channel_id=1, multi_channel=False, diarization=False, chunk_duration_sec=0.25):
        """
        Main streaming loop. Translates audio chunks into a stream of TranscriptionEvents.
        """
        await self._get_or_create_recognizer()
        
        # 1. Configure Features based on Model Profile
        # Profile: Chirp-3 (Large Speech Model)
        if self.is_chirp:
            features = cs_v2.RecognitionFeatures(
                enable_word_time_offsets=False, # Not supported in streaming
                enable_automatic_punctuation=True,
                multi_channel_mode=cs_v2.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if multi_channel else None
            )
        else:
            # Profile: Telephony / Standard
            features = cs_v2.RecognitionFeatures(
                enable_word_time_offsets=True,
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
            language_codes=["en-US"] # Fixed to English for this demo
        )

        streaming_config = cs_v2.StreamingRecognitionConfig(
            config=config,
            streaming_features={
                "interim_results": True,
                "enable_voice_activity_events": True
            }
        )

        # 2. Setup bi-directional stream
        async def request_generator():
            yield cs_v2.StreamingRecognizeRequest(recognizer=self.recognizer_name, streaming_config=streaming_config)
            
            chunks_sent = 0
            async for chunk in audio_gen:
                chunks_sent += 1
                self.current_audio_time = chunks_sent * chunk_duration_sec
                yield cs_v2.StreamingRecognizeRequest(audio=chunk)

        responses = await self.client.streaming_recognize(requests=request_generator())
        
        # 3. Yield standardized events
        async for response in responses:
            # Handle Voice Activity Detection (VAD)
            if response.speech_event_type:
                ev_name = cs_v2.StreamingRecognizeResponse.SpeechEventType(response.speech_event_type).name
                
                # USE THE API'S OFFSET IF PROVIDED
                event_time = self.current_audio_time
                if response.speech_event_offset:
                    event_time = response.speech_event_offset.total_seconds()

                yield TranscriptionEvent(
                    speaker_id=channel_id, text="", 
                    start_sec=event_time, end_sec=event_time,
                    is_final=True, event_type=ev_name.lower()
                )

            # Handle Transcripts
            for result in response.results:
                if not result.alternatives: continue
                alt = result.alternatives[0]
                
                speaker = channel_id
                if multi_channel: 
                    speaker = result.channel_tag
                elif diarization and alt.words: 
                    speaker = alt.words[0].speaker_tag

                # Timing logic: use words if available, fallback to clock for wordless models (Chirp)
                start = self.current_audio_time - 1.0 # Default 1s window if wordless
                if alt.words:
                    start = alt.words[0].start_offset.total_seconds()
                
                end = self.current_audio_time
                if alt.words:
                    end = alt.words[-1].end_offset.total_seconds()

                yield TranscriptionEvent(
                    speaker_id=speaker,
                    text=alt.transcript,
                    start_sec=max(0.0, start),
                    end_sec=end,
                    is_final=result.is_final,
                    words=[{
                        "word": w.word, 
                        "start": w.start_offset.total_seconds(),
                        "end": w.end_offset.total_seconds()
                    } for w in alt.words]
                )

class V1Provider:
    """
    Wraps Google STT V1 API. 
    Maintained primarily for comparing legacy AI Diarization on mono files.
    """
    def __init__(self, client: cs_v1.SpeechAsyncClient):
        self.client = client
        self.current_audio_time = 0.0

    async def stream(self, audio_gen):
        """Legacy streaming loop for V1 Diarization."""
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

        async def request_generator():
            yield cs_v1.StreamingRecognizeRequest(streaming_config=streaming_config)
            chunks_sent = 0
            async for chunk in audio_gen:
                chunks_sent += 1
                self.current_audio_time = chunks_sent * 0.25
                yield cs_v1.StreamingRecognizeRequest(audio_content=chunk)

        responses = await self.client.streaming_recognize(requests=request_generator())
        
        async for response in responses:
            if not response.results: continue
            result = response.results[0]
            if not result.alternatives: continue
            alt = result.alternatives[0]

            if result.is_final:
                if alt.words:
                    current_speaker = alt.words[0].speaker_tag
                    current_text = []
                    current_start = alt.words[0].start_time.total_seconds()
                    
                    for word in alt.words:
                        if word.speaker_tag != current_speaker:
                            yield TranscriptionEvent(
                                speaker_id=current_speaker, text=" ".join(current_text),
                                start_sec=current_start, end_sec=word.start_time.total_seconds(),
                                is_final=True
                            )
                            current_speaker, current_text, current_start = word.speaker_tag, [word.word], word.start_time.total_seconds()
                        else:
                            current_text.append(word.word)
                    
                    if current_text:
                        yield TranscriptionEvent(
                            speaker_id=current_speaker, text=" ".join(current_text),
                            start_sec=current_start, end_sec=alt.words[-1].end_time.total_seconds(),
                            is_final=True
                        )
                else:
                    yield TranscriptionEvent(speaker_id=1, text=alt.transcript, start_sec=self.current_audio_time - 1.0, end_sec=self.current_audio_time, is_final=True)
            else:
                if alt.transcript.strip():
                    yield TranscriptionEvent(speaker_id=1, text=alt.transcript, start_sec=self.current_audio_time, end_sec=self.current_audio_time, is_final=False)
