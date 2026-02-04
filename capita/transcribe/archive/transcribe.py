import argparse
import asyncio
import datetime
import json
import logging
import os
import io

from pydub import AudioSegment
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from google.cloud.storage import Client as StorageClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Environment Settings ---
# Load environment variables from a .env file if it exists.
load_dotenv()

# Fetch settings from environment variables
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us-central1")
GCP_RECOGNIZER_ID = os.getenv("GCP_RECOGNIZER_ID")
GCP_TRANSCRIPTION_MODEL = os.environ.get("GCP_TRANSCRIPTION_MODEL", "telephony")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-US")
CUSTOMER_CHANNEL = os.environ.get("CUSTOMER_CHANNEL", "channel_1")
OUTPUT_FILENAME = "output.json"


# A simple check for the most important settings.
assert GCP_PROJECT_ID, "🚨 PROJECT_ID not found in .env file."
assert GCP_RECOGNIZER_ID, "🚨 GCP_RECOGNIZER_ID not found in .env file."

# --- Constants ---
ENCODING_MAPPINGS = {
    "pcm": cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
    "wav": cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
}

class AudioStream:
    """A class to manage the audio stream and its properties."""
    def __init__(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

class TranscriptionService:
    """Service to transcribe audio using Google Cloud Speech-to-Text."""

    def __init__(self, gcs_uri: str, customer_channel: str, buffer_timeout: float):
        self.gcs_uri = gcs_uri
        self.customer_channel = customer_channel
        self.buffer_timeout = buffer_timeout
        self.transcribe_client = cs.SpeechAsyncClient(
            client_options=ClientOptions(
                api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com"
            )
        )
        self.gcp_transcription_model = GCP_TRANSCRIPTION_MODEL
        self.language_code = LANGUAGE_CODE
        self.enable_channel_identification = True
        self.media_sample_rate_hz = 0  # Will be determined from WAV file
        self.number_of_channels = 0    # Will be determined from WAV file
        self.audio_q = asyncio.Queue()
        self.full_transcript = ""
        self.accumulated_transcript_chunks = []
        self.accumulated_length = 0
        self.stream = AudioStream()
        self.audio_data = None # To hold the audio data in memory



    async def _get_audio_properties(self):
        """Reads the WAV file from GCS to determine audio properties."""
        try:
            storage_client = StorageClient()
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Use pydub to handle more audio formats like μ-law
            # Download once and store in memory
            self.audio_data = blob.download_as_bytes()
            
            # Use pydub to read properties from the in-memory data
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data))
            if audio_segment.channels == 2:
                left, right = audio_segment.split_to_mono()
                if left.raw_data == right.raw_data:
                    logger.info("Both audio channels are identical. Treating as mono.")
                    mono_audio = audio_segment.set_channels(1)
                    # The audio data needs to be updated to the mono version
                    # so that _stream_audio_from_gcs uses the correct data.
                    self.audio_data = mono_audio.export(format="wav").read()
                    self.number_of_channels = 1
                    self.enable_channel_identification = False
                else:
                    self.number_of_channels = 2
            else:
                self.number_of_channels = audio_segment.channels
                self.enable_channel_identification = False

            self.media_sample_rate_hz = audio_segment.frame_rate
            logger.info(f"Audio properties: {self.number_of_channels} channels, {self.media_sample_rate_hz} Hz, enable_channel_identification: {self.enable_channel_identification}")
        except Exception as e:
            logger.error(f"Failed to read audio properties from GCS: {e}")
            raise
        finally:
            storage_client.close()

    async def _stream_audio_from_gcs(self):
        """Downloads and streams a WAV file from GCS into the audio queue."""
        try:
            # Convert the audio to raw PCM (LINEAR16) data which the API expects
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data)) # type: ignore 
            audio_segment = audio_segment.set_sample_width(2)
            pcm_data = audio_segment.set_frame_rate(self.media_sample_rate_hz).set_channels(self.number_of_channels).raw_data

            # Stream the converted PCM data from memory
            chunk_size = 8000
            for i in range(0, len(pcm_data), chunk_size):
                chunk = pcm_data[i:i+chunk_size]
                if not chunk:
                    break
                await self.audio_q.put(chunk)

            await self.audio_q.put(None) # Signal end of stream
            logger.info("Finished streaming audio from GCS.")

        except Exception as e:
            logger.error(f"Error streaming from GCS: {e}")
            await self.audio_q.put(None)

    # Request generator function    
    async def request_generator(self):
            multi_channel_config = (
                cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
                if self.enable_channel_identification
                else cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
            )
            encoding = ENCODING_MAPPINGS.get("pcm", None)
            # Initial config request (REQUIRED)
            yield cs.StreamingRecognizeRequest(
                recognizer=self.recognizer,
                streaming_config=cs.StreamingRecognitionConfig(
                    config=cs.RecognitionConfig(
                        explicit_decoding_config=cs.ExplicitDecodingConfig(
                            encoding=encoding,
                            sample_rate_hertz=self.media_sample_rate_hz,
                            audio_channel_count=self.number_of_channels,
                        ),
                        features=cs.RecognitionFeatures(
                            multi_channel_mode=multi_channel_config,
                            enable_word_time_offsets=True,
                            enable_automatic_punctuation=True,
                            interim_results=True,
                            enable_word_confidence=True
                        ),
                        language_codes=[self.language_code],
                        model=self.gcp_transcription_model,
                    ),
                ),
            )

            # Audio chunks
            while True:
                chunk = await self.audio_q.get()
                if chunk is None:
                    logger.info("Chunk Empty..")
                    return
                yield cs.StreamingRecognizeRequest(audio=chunk)

    ## Transcription event handle function   
    async def _handle_transcription(self):
        responses = await self.transcribe_client.streaming_recognize(
            requests=self.request_generator()
        )
        async for response in responses:
            for result in response.results:
                if not result.alternatives:
                    continue
                alt = result.alternatives[0]

                if result.is_final:
                    if not alt.words:
                        continue
                    logger.debug(f"Final result:{result.alternatives[0].transcript}")
                    assert (
                        result.alternatives is not None and len(result.alternatives) > 0
                    ), "No alternatives found in result."

                    self.full_transcript += "\n" + result.alternatives[0].transcript
                    #BH CHange
                    # Default channel_tag to 1 if it doesn't exist (for single-channel audio)
                    channel_tag = result.channel_tag if result.channel_tag else 1
                    if channel_tag:
                        # Use result_end_offset if available, otherwise fall back to the end_offset of the last word.
                        end_time = getattr(  # noqa: F841
                            result, "result_end_offset", None
                        ) or getattr(result, "end_time", None)
                        if not end_time and alt.words:
                            end_time = alt.words[-1].end_offset
 
                        seconds = end_time.total_seconds() #type: ignore
                        result_end_dt = self.stream.start_time + datetime.timedelta(seconds=seconds)
                        # Based on the env the audio channels of customer and agent will set
                        if self.customer_channel.lower() == "channel_1":
                            self.accumulated_transcript_chunks.append(
                            {
                                "speaker": (
                                    "customer"
                                    if result.channel_tag == 1
                                    else "agent"
                                ),
                                "text": result.alternatives[0].transcript,
                                "timestamp": result_end_dt.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }
                            )
                        else:
                            self.accumulated_transcript_chunks.append(
                            {
                                "speaker": (
                                    "customer"
                                    if result.channel_tag == 2
                                    else "agent"
                                ),
                                "text": result.alternatives[0].transcript,
                                "timestamp": result_end_dt.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            }
                            )
                        logger.debug(f"{self.stream.start_time + datetime.timedelta(seconds=seconds)}: channel_{result.channel_tag }")
                        self.accumulated_length += len(
                        result.alternatives[0].transcript.split()
                        )

    def _process_result_buffer(self, buffer):
        if not buffer:
            return []
        
        buffer_transcript_chunks = []

        for result in buffer:
            if not result.alternatives:
                continue
            alt = result.alternatives[0]

            if not alt.words:
                continue
            logger.debug(f"Buffered Final result: {result.alternatives[0].transcript}")
            assert (
                result.alternatives is not None and len(result.alternatives) > 0
            ), "No alternatives found in result."

            self.full_transcript += "\n" + result.alternatives[0].transcript
            
            # Default channel_tag to 1 if it doesn't exist (for single-channel audio)
            channel_tag = getattr(result, 'channel_tag', 1)

            # Use result_end_offset if available, otherwise fall back to the end_offset of the last word.
            end_time = getattr(result, "result_end_offset", None)
            if not end_time and alt.words:
                end_time = alt.words[-1].end_offset

            seconds = end_time.total_seconds() # type: ignore
            result_end_dt = self.stream.start_time + datetime.timedelta(seconds=seconds)

            if self.enable_channel_identification:
                if self.customer_channel.lower() == "channel_1":
                    buffer_transcript_chunks.append(
                    {
                        "speaker": ("customer" if channel_tag == 1 else "agent"),
                        "text": result.alternatives[0].transcript,
                        "timestamp": result_end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    )
                else:
                    buffer_transcript_chunks.append(
                    {
                        "speaker": ("customer" if channel_tag == 2 else "agent"),
                        "text": result.alternatives[0].transcript,
                        "timestamp": result_end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    )
                self.accumulated_length += len(result.alternatives[0].transcript.split())
        
        # Create a copy to compare against after sorting
        original_chunks = list(buffer_transcript_chunks)
        sorted_chunks = sorted(original_chunks, key=lambda x: x['timestamp'])
 
        if original_chunks != sorted_chunks:
            # Calculate how many items were not in their correct sorted position.
            out_of_order_count = sum(1 for i, j in zip(original_chunks, sorted_chunks) if i != j)
            logger.info(f"{out_of_order_count} buffer transcript chunks were out of order from a total of {len(original_chunks)} and have been sorted by timestamp.")
        else:
            logger.info("The buffer transcript chunks did not need to be sorted")

        return sorted_chunks


    async def _handle_buffered_transcription(self):
        responses = await self.transcribe_client.streaming_recognize(
            requests=self.request_generator()
        )
        
        buffer = []
        BUFFER_TIMEOUT = self.buffer_timeout

        async def buffer_processor():
            while True:
                await asyncio.sleep(BUFFER_TIMEOUT)
                if buffer:
                    processed_chunks = self._process_result_buffer(buffer)
                    self.accumulated_transcript_chunks.extend(processed_chunks)
                    buffer.clear()
        
        processor_task = asyncio.create_task(buffer_processor())

        try:
            async for response in responses:
                for result in response.results:
                    if result.is_final:
                        buffer.append(result)
        finally:
            processor_task.cancel()
            # process any remaining items in the buffer
            processed_chunks = self._process_result_buffer(buffer)
            self.accumulated_transcript_chunks.extend(processed_chunks)
            buffer.clear()

    def _format_output(self):
        """Formats the transcript chunks into the desired JSON structure."""
        # Create a copy to compare against after sorting
        original_chunks = list(self.accumulated_transcript_chunks)
        sorted_chunks = sorted(original_chunks, key=lambda x: x['timestamp'])
 
        if original_chunks != sorted_chunks:
            # Calculate how many items were not in their correct sorted position.
            out_of_order_count = sum(1 for i, j in zip(original_chunks, sorted_chunks) if i != j)
            logger.info(f"{out_of_order_count} transcript chunks were out of order from a total of {len(original_chunks)} and have been sorted by timestamp.")
        else:
            logger.info("The transcript chunks did not need to be sorted")
 
        return sorted_chunks
    
    
    async def find_or_create_recognizer(self, recognizer_id: str ) -> cs.Recognizer:
        """Creates a recognizer with a unique ID and default recognition configuration.
        Args:
            recognizer_id (str): The unique identifier for the recognizer to be created.
        Returns:
            cloud_speech.Recognizer: The created recognizer object with configuration.
        """
        logger.info("Creating recognizer...")
        get_request = cs.GetRecognizerRequest(
            name=f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}/recognizers/{recognizer_id}"
        )

        create_request = cs.CreateRecognizerRequest(
            parent=f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}",
            recognizer_id=recognizer_id,
            recognizer=cs.Recognizer(
                default_recognition_config=cs.RecognitionConfig(
                    language_codes=["en-US"], model=GCP_TRANSCRIPTION_MODEL
                ),
            ),
        )
        #try to get it
        try:
            recognizer = await self.transcribe_client.get_recognizer(get_request)
            # A recognizer can exist but be in a DELETING or FAILED state.
            if recognizer.state == cs.Recognizer.State.ACTIVE:
                logger.info(f"Found active recognizer: {recognizer.name}")
                return recognizer
            else:
                logger.warning(f"Found recognizer '{recognizer.name}' but it is in state '{recognizer.state.name}'. Will proceed to create a new one.")
                # Treat non-active recognizers as if they were not found.
                raise exceptions.NotFound("Recognizer is not in an ACTIVE state.")
        except exceptions.NotFound:
            logger.info(f"Recognizer '{recognizer_id}' not found, creating it...")
            try:
                operation = await self.transcribe_client.create_recognizer(request=create_request) # type: ignore
                recognizer = await operation.result()
                logger.info(f"Successfully created recognizer: {recognizer.name}")
                return recognizer
            except Exception as e:
                logger.error(f"Failed to create recognizer: {e}")
                raise
        except exceptions.PermissionDenied as e:
            logger.warning(f"Permission denied creating recognizer '{recognizer_id}', possibly due to recent deletion. Retrying with a unique ID. Original error: {e}")
            # This can happen if the recognizer was recently deleted and the name is not yet available.
            # We'll try creating it again with a unique suffix.
            unique_recognizer_id = f"{recognizer_id}-{int(datetime.datetime.now().timestamp())}"
            create_request.recognizer_id = unique_recognizer_id
            operation = await self.transcribe_client.create_recognizer(request=create_request) # type: ignore
            recognizer = await operation.result()
            logger.info(f"Successfully created recognizer with unique ID: {recognizer.name}")
            return recognizer

    async def run(self, use_buffered: bool = False):
        """Runs the transcription process."""
        global GCP_RECOGNIZER_ID

        new_recognizer = await self.find_or_create_recognizer(recognizer_id=GCP_RECOGNIZER_ID) # type: ignore
        self.recognizer = new_recognizer.name
        logger.info(f"Using recognizer: {self.recognizer}")

        logger.info("Getting audio properties...")
        await self._get_audio_properties()

        logger.info("Starting transcription process...")
        streamer_task = asyncio.create_task(self._stream_audio_from_gcs())
        if use_buffered:
            handler_task = asyncio.create_task(self._handle_buffered_transcription())
        else:
            handler_task = asyncio.create_task(self._handle_transcription())

        await asyncio.gather(streamer_task, handler_task)

        logger.info("Transcription process finished.")
        logger.info(f"Full transcript: {self.full_transcript}")

        formatted_output = self._format_output()
        
        # Save to file
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(formatted_output, f, indent=2)
        logger.info(f"Transcription output saved to {OUTPUT_FILENAME}")


async def main():
    """Main function to run the transcription service."""

        
    parser = argparse.ArgumentParser(description="Transcribe an audio file from GCS.")
    parser.add_argument(
        "gcs_uri",
        help="The GCS URI of the audio file to transcribe (e.g., gs://bucket/file.mp3 or gs://bucket/file.wav)",
    )
    parser.add_argument(
        "--customer-channel",
        default=os.environ.get("CUSTOMER_CHANNEL", "channel_1"),
        help="The channel of the customer's audio. Can be 'channel_1' or 'channel_2'.",
    )
    parser.add_argument(
        '--use-buffered', 
        action='store_true', 
        help='Enable to use the buffered transcription handler.'
    )
    parser.add_argument(
        '--buffer-timeout',
        type=float,
        default=0.5,
        help='Timeout in seconds for the buffered transcription handler to flush results.'
    )
    args = parser.parse_args()

    transcription_service = TranscriptionService(gcs_uri=args.gcs_uri, customer_channel=args.customer_channel, buffer_timeout=args.buffer_timeout)
    await transcription_service.run(args.use_buffered)


    print(f"Transcription output from {OUTPUT_FILENAME}:")
    with open(OUTPUT_FILENAME, "r") as f:
        print(f.readlines())


if __name__ == "__main__":
    asyncio.run(main())
