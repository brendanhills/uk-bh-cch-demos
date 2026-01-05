import math
from typing import Iterator
from pydub import AudioSegment
from io import BytesIO

from google.api_core.client_options import ClientOptions
from google.cloud import storage
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

# 100 ms chuck size as per https://cloud.google.com/speech-to-text/v2/docs/best-practices#frame_size
CHUNK_SIZE_SECS = 0.100
# A common buffer size (4KB) to read enough initial bytes for audio libraries
HEADER_READ_BYTES = 4096

def generate_requests(
    stream_file: str
) -> Iterator[cloud_speech.StreamingRecognizeRequest]:

    gcs_client = storage.Client()
    bucket_name, blob_name = stream_file[len("gs://"):].split("/", 1)
    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    audio_file_stream = blob.open("rb")

    header_bytes = audio_file_stream.read(HEADER_READ_BYTES)
    audio_file_stream.seek(0)
    audio = AudioSegment.from_file(BytesIO(header_bytes)) # type: ignore

    if not audio:
        raise ValueError("Could not read audio file from GCS.")

    max_chunk_size_bytes = math.ceil(audio.frame_rate * audio.channels * audio.sample_width * CHUNK_SIZE_SECS)

    yield cloud_speech.StreamingRecognizeRequest(
        recognizer="projects/uk-bh-experiments-argolis/locations/us/recognizers/_",
        streaming_config=cloud_speech.StreamingRecognitionConfig(
            streaming_features = cloud_speech.StreamingRecognitionFeatures(
                enable_voice_activity_events=True,
                interim_results=True,
            ),
            config=cloud_speech.RecognitionConfig(
                features=cloud_speech.RecognitionFeatures(
                    #enable_word_time_offsets=True,
                    diarization_config=cloud_speech.SpeakerDiarizationConfig(
                        min_speaker_count=0,
                        max_speaker_count=0,
                    ),
                ),
                explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
                    encoding="LINEAR16",
                    sample_rate_hertz=16000,
                    audio_channel_count=1
                ),
                model="chirp_3",
                language_codes=["auto"],
            ),
        ),
    )
    while True:
        chunk = audio_file_stream.read(max_chunk_size_bytes)
        if not chunk:
            break
        yield cloud_speech.StreamingRecognizeRequest(audio=chunk)

def transcribe_streaming_v2(
    stream_file:str,
) -> list[cloud_speech.StreamingRecognizeResponse]:

    speech_client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint="us-speech.googleapis.com"
        )
    )

    responses_iterator = speech_client.streaming_recognize(requests=generate_requests(stream_file))
    responses = []
    for response in responses_iterator:
        responses.append(response)
        for result in response.results:
            print(f"Transcript: {result.alternatives[0].transcript}")

    return responses

stream_file = "gs://uk-bh-experiments-argolis-us/capita/speech_medical_conversation_2.wav"
print(transcribe_streaming_v2(stream_file))