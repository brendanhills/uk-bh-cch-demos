import asyncio
import argparse
import datetime
import logging
import textwrap
import time

from google.cloud import speech_v1 as speech
from transcribe_common import BaseTranscriptionService

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MonoTranscriptionServiceV1(BaseTranscriptionService):
    """Service for streaming audio transcription with Google Cloud Speech-to-Text V1."""

    def __init__(self, gcs_uri: str, buffer_timeout: float = 0.5):
        # Force mono for V1 Diarization to ensure we mix both channels
        super().__init__(gcs_uri, buffer_timeout, force_mono=True)
        self.client = speech.SpeechAsyncClient()

    async def generate_requests(self):
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
        while True:
            if time.time() - start_time > 240:
                return

            chunk = await self.audio_q.get()
            if chunk is None: 
                self.stream_finished_flag = True
                return
            
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    async def process_responses(self, stream, use_buffered=False):
        """Consumes responses from the API."""
        buffer = []

        async def flush_buffer_loop():
            while True:
                await asyncio.sleep(self.buffer_timeout)
                if buffer:
                    if self.last_was_heartbeat:
                        print("", flush=True)
                        self.last_was_heartbeat = False
                    self._process_buffer(buffer)
                    buffer.clear()

        flusher = asyncio.create_task(flush_buffer_loop()) if use_buffered else None

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
                
                # Clear any lingering interim text before printing final result
                self._clear_interim_output()

                if not use_buffered:
                    if self.last_was_heartbeat:
                        # print("", flush=True) # No longer needed with clear_interim
                        self.last_was_heartbeat = False
                    self._process_single_result(result)
                else:
                    buffer.append(result)
        finally:
            if flusher: flusher.cancel() 
            self._clear_interim_output() # Clean up at the end
            if buffer: 
                if self.last_was_heartbeat:
                    print("", flush=True)
                    self.last_was_heartbeat = False
                self._process_buffer(buffer)

    def _print_chunk(self, chunk):
        # Override Base to use V1 specific fields and layout
        should_print, mod_chunk, chunk_type = self._should_print_chunk(chunk)
        if not should_print or chunk_type == "IGNORE":
            return

        speaker_tag = mod_chunk.get("speaker_tag", 1) 
        text = mod_chunk.get("text", "") 
        timestamp = mod_chunk.get("timestamp", "") 
        speaker_label = f"Speaker {speaker_tag}"
        
        # Determine prefix based on type
        prefix = ""
        if chunk_type == "CORRECTION":
            prefix = "[CORRECTION] "
        elif chunk_type == "EXTENSION":
            prefix = "... "
        elif chunk_type == "RE-ATTRIBUTION":
            prefix = "\033[1;31m[RE-ATTRIBUTED]\033[0m "
            
        # Apply Colors
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
            # Normalize keys for Base dedupe if needed, though V1 uses 'speaker_tag'
            "speaker": speaker_tag, 
            "timestamp_float": seconds
        }

    def _process_single_result(self, result):
        chunks = self._extract_chunks_from_result(result)
        for chunk in chunks:
            self.transcript_chunks.append(chunk)
            self._print_chunk(chunk)

    def _process_buffer(self, buffer):
        all_chunks = []
        for result in buffer:
            all_chunks.extend(self._extract_chunks_from_result(result))
        
        all_chunks.sort(key=lambda x: x['sort_key'])
        
        for chunk in all_chunks:
            self._print_chunk(chunk)
            self.transcript_chunks.append(chunk)

    async def run(self, use_buffered=False, wait_for_play=False):
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.stream_finished_flag = False
        
        self._generate_signed_url()
        
        await self.prepare_audio()

        if wait_for_play:
            self.wait_for_user_start()
            self.start_time = datetime.datetime.now(datetime.timezone.utc)

        if not self.audio_bytes:
            logger.error("No audio data to transcribe!")
            return

        logger.info(f"Starting V1 {'buffered' if use_buffered else 'live'} transcription...")
        
        stream_task = asyncio.create_task(self.stream_audio_chunks())
        await asyncio.sleep(0.5)

        while not self.stream_finished_flag:
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests()
                )
                await self.process_responses(responses_stream, use_buffered)
            except Exception as e:
                logger.error(f"Error during streaming_recognize: {e}")
                await asyncio.sleep(1)
        
        await stream_task 

async def main():
    parser = argparse.ArgumentParser(description="Transcribe mono audio with V1 Diarization.")
    parser.add_argument("gcs_uri", help="The GCS URI")
    parser.add_argument('--use-buffered', action='store_true', help='Enable buffered.')
    parser.add_argument('--buffer-timeout', type=float, default=5.0)
    parser.add_argument('--wait-for-play', action='store_true', help='Wait for user input before starting stream.')
    args = parser.parse_args()

    print(f"{'Speaker 1':<60} {'Speaker 2'}")
    print("-" * 100)

    service = MonoTranscriptionServiceV1(args.gcs_uri, args.buffer_timeout)
    await service.run(args.use_buffered, args.wait_for_play)

if __name__ == "__main__":
    asyncio.run(main())
