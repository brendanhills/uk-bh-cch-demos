"""
Specialized provider for Google Chirp-3.
Handles auto-language detection and the lack of word-level timestamps.
"""

from google.cloud import speech_v2 as cs_v2
from .providers import V2Provider
from .models import TranscriptionEvent

class Chirp3Provider(V2Provider):
    """
    Extends V2Provider with Chirp-3 specific configuration.
    """
    def __init__(self, client: cs_v2.SpeechAsyncClient, recognizer_name: str, model: str = "chirp-3"):
        super().__init__(client, recognizer_name, model)
        # Chirp-3 currently doesn't support word-level offsets in streaming the same way as telephony
        self.is_chirp = True 

    async def stream(self, audio_gen, channel_id=1, multi_channel=False, diarization=False, chunk_duration_sec=0.25):
        """
        Specialized streaming for Chirp-3.
        """
        await self._get_or_create_recognizer()
        
        # Chirp-3 specific features
        features = cs_v2.RecognitionFeatures(
            enable_word_time_offsets=False, # Chirp-3 limitation in streaming
            enable_automatic_punctuation=True,
            multi_channel_mode=cs_v2.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if multi_channel else None
        )
        
        # Note: Diarization is usually not used with multi-channel or specialized Chirp-3 paths
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
            language_codes=["auto"] # Specialized for Chirp-3 auto-detection
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
            if response.speech_event_type:
                ev_name = cs_v2.StreamingRecognizeResponse.SpeechEventType(response.speech_event_type).name
                yield TranscriptionEvent(
                    speaker_id=channel_id, text="", 
                    start_sec=self.current_audio_time, end_sec=self.current_audio_time,
                    is_final=True, event_type=ev_name.lower()
                )

            for result in response.results:
                if not result.alternatives: continue
                alt = result.alternatives[0]
                
                speaker = channel_id
                if multi_channel: 
                    speaker = result.channel_tag

                # Chirp-3 often lacks word-level timestamps, so we use current_audio_time as a fallback
                # This will be refined in the Engine track for better interleaving
                start = self.current_audio_time - 1.0 # Rough estimate if wordless
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
