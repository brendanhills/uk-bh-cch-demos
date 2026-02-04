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

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MonoTranscriptionServiceV1(BaseTranscriptionService):
    """Service for streaming audio transcription with Google Cloud Speech-to-Text V1."""

    def __init__(self, sample_rate: int, channels: int):
        super().__init__(sample_rate, channels)
        self.client = speech.SpeechAsyncClient()
        self.speaker_history = {} 

    async def generate_requests(self, audio_stream):
        """Yields streaming requests for the V1 API."""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="en-US",
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2,
            ),
            model="phone_call",
            use_enhanced=True,
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        start_time = time.time()
        # Iterate over the provided audio stream
        async for chunk in audio_stream:
            if time.time() - start_time > 240:
                return
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    async def process_responses(self, stream):
        """Consumes responses from the API."""
        try:
            async for response in stream:
                if not response.results:
                    continue
                
                result = response.results[0]
                if not result.alternatives:
                    continue

                if not result.is_final:
                    if result.alternatives:
                        text = result.alternatives[0].transcript
                        self._clear_interim_output()
                        self._print_interim_output(text)
                    self.last_was_heartbeat = True
                    continue
                
                self._clear_interim_output()

                if self.last_was_heartbeat:
                    self.last_was_heartbeat = False
                self._process_single_result(result)
        finally:
            self._clear_interim_output() 

    def _should_print_chunk(self, chunk):
        """Deduplicates chunks based on history (V1 specific)."""
        speaker = chunk.get('speaker', 'Unknown')
        ts = chunk.get('timestamp_float', 0.0)
        text = chunk.get('text', '').strip()
        
        if speaker not in self.speaker_history:
            self.speaker_history[speaker] = []
        history = self.speaker_history[speaker]
        
        # Check against recent history
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

        # Check other speakers for re-attribution
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
        should_print, mod_chunk, chunk_type = self._should_print_chunk(chunk)
        if not should_print or chunk_type == "IGNORE":
            return

        speaker_tag = mod_chunk.get("speaker_tag", 1) 
        text = mod_chunk.get("text", "") 
        timestamp = mod_chunk.get("timestamp", "") 
        speaker_label = f"Speaker {speaker_tag}"
        
        prefix = ""
        if chunk_type == "CORRECTION":
            prefix = "[CORRECTION] "
        elif chunk_type == "EXTENSION":
            prefix = "... "
        elif chunk_type == "RE-ATTRIBUTION":
            prefix = "\033[1;31m[RE-ATTRIBUTED]\033[0m "
            
        color = self.COLOR_SPEAKER_1 if speaker_tag == 1 else self.COLOR_SPEAKER_2
        colored_text = f'{color}"{text}"{self.COLOR_RESET}'
            
        full_content = f'{timestamp} [{speaker_label}] {prefix}{colored_text}'
        
        LEFT_COL_WIDTH = 45 
        RIGHT_COL_OFFSET = 60 
        
        if speaker_tag == 1:
            indent_str = " " * 12 
            wrapper = textwrap.TextWrapper(width=LEFT_COL_WIDTH, subsequent_indent=indent_str)
            print(wrapper.fill(full_content), flush=True)
        else:
            offset_str = " " * RIGHT_COL_OFFSET
            wrapper = textwrap.TextWrapper(width=RIGHT_COL_OFFSET + LEFT_COL_WIDTH, 
                                         initial_indent=offset_str, 
                                         subsequent_indent=offset_str + " " * 12)
            print(wrapper.fill(full_content), flush=True)

    def _extract_chunks_from_result(self, result):
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
        ts = self.start_time + datetime.timedelta(seconds=seconds) 
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
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
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.stream_finished_flag = False
        
        logger.info(f"Starting V1 live transcription...")
        
        try:
            responses_stream = await self.client.streaming_recognize(
                requests=self.generate_requests(audio_stream)
            )
            await self.process_responses(responses_stream)
        except Exception as e:
            logger.error(f"Error during streaming_recognize: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Transcribe mono audio with V1 Diarization.")
    parser.add_argument("gcs_uri", help="The GCS URI")
    parser.add_argument('--wait-for-play', action='store_true', help='Wait for user input before starting stream.')
    args = parser.parse_args()

    print(f"{'Speaker 1':<60} {'Speaker 2'}")
    print("-" * 100)

    # 1. Setup Simulator
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=True)
    await simulator.prepare()
    simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()

    # 2. Setup Service
    service = MonoTranscriptionServiceV1(simulator.sample_rate, simulator.channels)
    
    # 3. Run
    await service.run(simulator.stream())

if __name__ == "__main__":
    asyncio.run(main())