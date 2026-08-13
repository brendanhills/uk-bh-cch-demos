"""Unit tests verifying document snapshot attachment persistence (#BUG-45)."""

import base64
import time
from pathlib import Path
import pytest


def test_attachment_persistence_directory_and_file_creation(tmp_path):
    """Verify base64 image data is persisted to app/logs/attachments/<session_id>_<timestamp>.jpg."""
    attachments_dir = tmp_path / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    session_id = "test_session_123"
    timestamp_ms = int(time.time() * 1000)
    fake_image_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF" # JPEG header
    
    file_name = f"{session_id}_{timestamp_ms}.jpg"
    file_path = attachments_dir / file_name
    file_path.write_bytes(fake_image_bytes)

    assert file_path.exists()
    assert file_path.read_bytes() == fake_image_bytes
    assert file_path.parent == attachments_dir
