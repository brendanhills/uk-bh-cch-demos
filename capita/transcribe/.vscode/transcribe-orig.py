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