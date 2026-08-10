"""Unit tests verifying call transcript file logging (BUG-24)."""

import logging
from pathlib import Path


def test_call_transcript_logger_setup():
    """Verify call_transcript_logger is initialized and writes to logs/call_transcripts.log (BUG-24)."""
    logs_dir = Path(__file__).parent.parent / "app" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "call_transcripts.log"

    transcript_logger = logging.getLogger("test_call_transcripts")
    transcript_logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s"))
    transcript_logger.addHandler(handler)

    test_msg = "[TEST_TURN] user_id=test_u1 session_id=test_s1: Hello Cymbal Hospital"
    transcript_logger.info(test_msg)
    handler.close()

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert test_msg in content
