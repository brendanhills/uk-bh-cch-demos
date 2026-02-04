"""
Mono Transcription Service (STT V1) with AI Diarization

This script demonstrates speaker separation when both parties are mixed onto a 
single audio channel. It uses voice fingerprinting (Diarization) to identify speakers.
"""

import asyncio
import argparse
import datetime
import logging
import textwrap
import time
import difflib

from google.cloud import speech_v1 as speech
from transcribe_common import BaseTranscriptionService
from simulate_audio import AudioStreamSimulator

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MonoTranscriptionServiceV1(BaseTranscriptionService):
    """
    Subclass using the STT V1 API. 
    Includes sophisticated deduplication logic to handle V1's iterative diarization updates.
    """

    def __init__(self, sample_rate: int, channels: int):
        super().__init__(sample_rate, channels)
        self.client = speech.SpeechAsyncClient()
        self.speaker_history = {} # Used for deduplication

    async def generate_requests(self, audio_stream):
        """Generates V1 API requests with phone-optimized diarization settings."""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="en-US",
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2,
            ),
            model="phone_call", # Enhanced model for high-accuracy phone calls
            use_enhanced=True,
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        start_time = time.time()
        async for chunk in audio_stream:
            # V1 has a strict session limit; we guard against hanging
            if time.time() - start_time > 300: 
                return
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    async def process_responses(self, stream):
        """Processes responses from the V1 API."""
        try:
            async for response in stream:
                if not response.results:
                    continue
                
                result = response.results[0]
                if not result.alternatives:
                    continue

                if not result.is_final:
                    # Show interim draft at the bottom
                    text = result.alternatives[0].transcript
                    self._clear_interim_output()
                    self._print_interim_output(text)
                    self.last_was_heartbeat = True
                    continue
                
                # Clear draft before printing permanent text
                self._clear_interim_output()
                if self.last_was_heartbeat:
                    self.last_was_heartbeat = False
                self._process_single_result(result)
        except Exception as e:
            logger.error(f"Error processing V1 stream: {e}")
        finally:
            self._clear_interim_output() 

    def _should_print_chunk(self, chunk):
        """
        V1 Diarization often 'corrects' itself by re-sending chunks.
        This method uses fuzzy matching to detect duplicates, corrections, 
        and speaker re-attributions to keep the output clean.
        """
        speaker = chunk.get('speaker', 'Unknown')
        ts = chunk.get('timestamp_float', 0.0)
        text = chunk.get('text', '').strip()
        
        if speaker not in self.speaker_history:
            self.speaker_history[speaker] = []
        history = self.speaker_history[speaker]
        
        # 1. Exact Duplicate or Incremental Update Check
        for i in range(len(history) - 1, max(-1, len(history) - 11), -1):
            prev_ts, prev_text = history[i]
            if abs(ts - prev_ts) < 0.5:
                if prev_text.startswith(text): return False, None, "IGNORE"
                if text.startswith(prev_text):
                    new_part = text[len(prev_text):].strip()
                    if not new_part: return False, None, "IGNORE"
                    history[i] = (ts, text) 
                    chunk['text'] = new_part
                    return True, chunk, "EXTENSION"
                history[i] = (ts, text)
                return True, chunk, "CORRECTION"

        # 2. Re-attribution Check (Checking if another speaker claimed this text)
        for other_tag, other_hist in self.speaker_history.items():
            if other_tag == speaker: continue
            for p_ts, p_text in other_hist[-10:]:
                matcher = difflib.SequenceMatcher(None, text.lower(), p_text.lower())
                match = matcher.find_longest_match(0, len(text), 0, len(p_text))
                if match.size > 10:
                    history.append((ts, text))
                    return True, chunk, "RE-ATTRIBUTION"

        history.append((ts, text))
        return True, chunk, "NEW"

    def _print_chunk(self, chunk):
        """Renders the finalized, deduplicated chunk in the columns."""
        should_print, mod_chunk, chunk_type = self._should_print_chunk(chunk)
        if not should_print or chunk_type == "IGNORE":
            return

        speaker_tag = mod_chunk.get("speaker_tag", 1) 
        text = mod_chunk.get("text", "") 
        timestamp = mod_chunk.get("timestamp", "") 
        speaker_label = f"Speaker {speaker_tag}"
        
        # UI Prefixing
        prefix = ""
        if chunk_type == "CORRECTION": prefix = "[CORRECTION] "
        elif chunk_type == "EXTENSION": prefix = "... "
        elif chunk_type == "RE-ATTRIBUTION": prefix = "\033[1;31m[RE-ATTRIBUTED]\033[0m "
            
        color = self.COLOR_SPEAKER_1 if speaker_tag == 1 else self.COLOR_SPEAKER_2
        colored_text = f'{color}"{text}"{self.COLOR_RESET}'
        full_content = f'{timestamp} [{speaker_label}] {prefix}{colored_text}'
        
        # Display in two columns based on speaker tag
        if speaker_tag == 1:
            wrapper = textwrap.TextWrapper(width=55, subsequent_indent=" " * 12)
            print(wrapper.fill(full_content), flush=True)
        else:
            offset = " " * 60
            wrapper = textwrap.TextWrapper(width=115, initial_indent=offset, subsequent_indent=offset + " " * 12)
            print(wrapper.fill(full_content), flush=True)

    def _extract_chunks_from_result(self, result):
        """Splits a single API result into speaker-indexed chunks."""
        chunks = []
        if not result.alternatives or not result.alternatives[0].words:
            return chunks

        words = result.alternatives[0].words
        current_speaker = words[0].speaker_tag
        current_transcript = []
        current_start_time = words[0].start_time.total_seconds()

        for word in words:
            if word.speaker_tag != current_speaker:
                chunks.append(self._create_chunk_dict(current_speaker, " ".join(current_transcript), current_start_time))
                current_speaker = word.speaker_tag
                current_transcript = [word.word]
                current_start_time = word.start_time.total_seconds()
            else:
                current_transcript.append(word.word)
        
        if current_transcript:
            chunks.append(self._create_chunk_dict(current_speaker, " ".join(current_transcript), current_start_time))
        return chunks

    def _create_chunk_dict(self, speaker_tag, text, seconds):
        """Helper to create standardized chunk dictionaries."""
        ts = self.start_time + datetime.timedelta(seconds=seconds) 
        timestamp = ts.strftime("%H:%M:%S.%f")[:-5]
        return {
            "speaker_tag": speaker_tag,
            "text": text,
            "timestamp": timestamp,
            "sort_key": seconds,
            "speaker": speaker_tag, 
            "timestamp_float": seconds
        }

    def _process_single_result(self, result):
        chunks = self._extract_chunks_from_result(result)
        for chunk in chunks:
            self.transcript_chunks.append(chunk)
            self._print_chunk(chunk)

    async def run(self, audio_stream):
        """Main execution flow for V1."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        logger.info(f"Starting V1 Mono Transcription demo...")
        try:
            responses_stream = await self.client.streaming_recognize(
                requests=self.generate_requests(audio_stream)
            )
            await self.process_responses(responses_stream)
        except Exception as e:
            logger.error(f"Stream error: {e}")

async def main():
    """CLI Entrypoint."""
    parser = argparse.ArgumentParser(description="Mono Transcription (V1 Diarization) Demo")
    parser.add_argument("gcs_uri", help="The GCS URI (gs://...)")
    parser.add_argument('--wait-for-play', action='store_true', help='Pauses for user to start audio.')
    args = parser.parse_args()

    print(f"\n{'Speaker 1':<60} {'Speaker 2'}")
    print("-" * 120)

    # Simulator: Forcing mono down-mix for V1 processing
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=True)
    await simulator.prepare()
    simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()

    service = MonoTranscriptionServiceV1(simulator.sample_rate, simulator.channels)
    await service.run(simulator.stream())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo stopped.")