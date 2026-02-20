"""
API Providers for Google Speech-to-Text (STT) V1 and V2.
These classes wrap the low-level GRPC streaming logic and yield standardized TranscriptionEvents.
"""

import asyncio
import datetime
from google.cloud import speech_v2 as cs_v2
from google.cloud import speech_v1 as cs_v1
from google.api_core.client_options import ClientOptions
from .models import TranscriptionEvent

class V2Provider:
    """
    Wraps Google STT V2 API. 
    Supports modern features like multi-channel recognition and voice activity events.
    """
    def __init__(self, client: cs_v2.SpeechAsyncClient, recognizer_name: str, model: str):
        self.client = client
        self.recognizer_name = recognizer_name
        self.model = model
        self.current_audio_time = 0.0
        self.is_chirp = "chirp" in model.lower()

    async def _get_or_create_recognizer(self):
        """Ensures the requested Recognizer exists in the GCP project."""
        try:
            return await self.client.get_recognizer(name=self.recognizer_name)
        except Exception:
            # Automatic creation if not found (useful for demo setup)
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
        """
        Main streaming loop. Translates audio chunks into a stream of TranscriptionEvents.
        """
        await self._get_or_create_recognizer()
        
        # Configure the recognition features
        features = cs_v2.RecognitionFeatures(
            enable_word_time_offsets=not self.is_chirp,
            enable_automatic_punctuation=True,
            multi_channel_mode=cs_v2.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if multi_channel else None
        )
        
        if diarization:
            # AI-based speaker separation (used for mono files)
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
                enable_voice_activity_events=True # Used for Active Blocking in Engine
            )
        )

        async def request_generator():
            # Initial request must contain the configuration
            yield cs_v2.StreamingRecognizeRequest(recognizer=self.recognizer_name, streaming_config=streaming_config)
            
            chunks_sent = 0
            async for chunk in audio_gen:
                chunks_sent += 1
                self.current_audio_time = chunks_sent * chunk_duration_sec
                yield cs_v2.StreamingRecognizeRequest(audio=chunk)

        # Execute the bi-directional stream
        responses = await self.client.streaming_recognize(requests=request_generator())
        
        async for response in responses:
            # 1. Handle Voice Activity (VAD) Events
            if response.speech_event_type:
                ev_name = cs_v2.StreamingRecognizeResponse.SpeechEventType(response.speech_event_type).name
                yield TranscriptionEvent(
                    speaker_id=channel_id, text="", 
                    start_sec=self.current_audio_time, end_sec=self.current_audio_time,
                    is_final=True, event_type=ev_name.lower()
                )

            # 2. Handle Transcript Results
            for result in response.results:
                if not result.alternatives: continue
                alt = result.alternatives[0]
                
                # Determine speaker attribution
                speaker = channel_id
                if multi_channel: 
                    speaker = result.channel_tag
                if diarization and alt.words: 
                    speaker = alt.words[0].speaker_tag

                # Calculate timing
                start = alt.words[0].start_offset.total_seconds() if alt.words else self.current_audio_time
                end = alt.words[-1].end_offset.total_seconds() if alt.words else (start + 1.0)

                yield TranscriptionEvent(
                    speaker_id=speaker,
                    text=alt.transcript,
                    start_sec=start,
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

        # Initial signal to UI
        yield TranscriptionEvent(speaker_id=1, text="", start_sec=0.0, end_sec=0.0, is_final=False, event_type="heartbeat")

        responses = await self.client.streaming_recognize(requests=request_generator())
        
        async for response in responses:
            if not response.results: continue
            result = response.results[0]
            if not result.alternatives: continue
            alt = result.alternatives[0]

            if result.is_final:
                if alt.words:
                    # Logic to group words by speaker to create natural turns immediately
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
