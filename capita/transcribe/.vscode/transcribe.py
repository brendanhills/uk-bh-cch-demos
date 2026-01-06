import argparse
import asyncio
import datetime
import json
import logging
import os
import io
import wave

from pydub import AudioSegment
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from google.cloud.speech_v2 import SpeechClient
from google.cloud import storage
from types import SimpleNamespace
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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

# Create a simple settings object to be compatible with the original _handle_transcription function
settings = SimpleNamespace(
    customer_channel=CUSTOMER_CHANNEL
)

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

    def __init__(self, gcs_uri: str):
        self.gcs_uri = gcs_uri
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
            storage_client = storage.Client()
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)

            # Use pydub to handle more audio formats like μ-law
            # Download once and store in memory
            self.audio_data = blob.download_as_bytes()
            
            # Use pydub to read properties from the in-memory data
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data))
            self.number_of_channels = audio_segment.channels
            self.media_sample_rate_hz = audio_segment.frame_rate
            logger.info(f"Audio properties: {self.number_of_channels} channels, {self.media_sample_rate_hz} Hz")
        except Exception as e:
            logger.error(f"Failed to read audio properties from GCS: {e}")
            raise

    async def _stream_audio_from_gcs(self):
        """Downloads and streams a WAV file from GCS into the audio queue."""
        try:
            # Convert the audio to raw PCM (LINEAR16) data which the API expects
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data))
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
                    logger.debug(f"Final result: {result.alternatives[0].transcript}")
                    assert (
                        result.alternatives is not None and len(result.alternatives) > 0
                    ), "No alternatives found in result."

                    self.full_transcript += "\n" + result.alternatives[0].transcript
                    if result.channel_tag:
                        end_time = getattr(  # noqa: F841
                            result, "result_end_offset", None
                        ) or getattr(result, "end_time", None)
                        seconds = end_time.total_seconds()
                        result_end_dt = self.stream.start_time + datetime.timedelta(seconds=seconds)
                        # Based on the env the audio channels of customer and agent will set
                        if settings.customer_channel.lower() == "channel_1":
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
                        self.accumulated_length += len(
                        result.alternatives[0].transcript.split()
                        )

    def _format_output(self):
        """Formats the transcript chunks into the desired JSON structure."""
        # Return the transcript chunks in the order they were received, without sorting or grouping.
        return self.accumulated_transcript_chunks
    
    
    async def create_recognizer(self, recognizer_id: str ) -> cs.Recognizer:
        """Creates a recognizer with a unique ID and default recognition configuration.
        Args:
            recognizer_id (str): The unique identifier for the recognizer to be created.
        Returns:
            cloud_speech.Recognizer: The created recognizer object with configuration.
        """
        logger.info("Creating recognizer...")
        # Instantiates a client
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
                operation = await self.transcribe_client.create_recognizer(request=create_request)
                recognizer = await operation.result()
                logger.info(f"Successfully created recognizer: {recognizer.name}")
                return recognizer
            except Exception as e:
                logger.error(f"Failed to create recognizer: {e}")
                raise

    async def run(self):
        """Runs the transcription process."""
        global GCP_RECOGNIZER_ID

        if GCP_RECOGNIZER_ID == "_":
            new_recognizer = await self.create_recognizer(recognizer_id="my-recognizer-telephony")
            self.recognizer = new_recognizer.name
        else:
            self.recognizer = self.transcribe_client.recognizer_path(GCP_PROJECT_ID, GCP_LOCATION, GCP_RECOGNIZER_ID)
        logger.info("Getting audio properties...")
        await self._get_audio_properties()

        logger.info("Starting transcription process...")
        streamer_task = asyncio.create_task(self._stream_audio_from_gcs())
        handler_task = asyncio.create_task(self._handle_transcription())

        await asyncio.gather(streamer_task, handler_task)

        logger.info("Transcription process finished.")
        logger.info(f"Full transcript: {self.full_transcript}")

        formatted_output = self._format_output()
        
        # Save to file
        output_filename = "output.json"
        with open(output_filename, "w") as f:
            json.dump(formatted_output, f, indent=2)
        logger.info(f"Transcription output saved to {output_filename}")


async def main():
    """Main function to run the transcription service."""

        
    parser = argparse.ArgumentParser(description="Transcribe a WAV file from GCS.")
    parser.add_argument(
        "gcs_uri",
        help="The GCS URI of the WAV file to transcribe (e.g., gs://bucket/file.wav)",
    )
    args = parser.parse_args()

    if not args.gcs_uri.startswith("gs://") or not args.gcs_uri.endswith(".wav"):
        logger.error("Please provide a valid GCS URI for a .wav file.")
        return

    transcription_service = TranscriptionService(gcs_uri=args.gcs_uri)
    await transcription_service.run()

if __name__ == "__main__":
    asyncio.run(main())
