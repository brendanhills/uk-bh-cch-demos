import os
import pytest
from google import genai
from src.gemini_assistant import init_client, stream_pdf_qa

@pytest.fixture
def sample_pdf_path():
    path = "data/bp1_bs-1.pdf"
    assert os.path.exists(path), f"Sample PDF not found at {path}"
    return path

def test_init_client():
    client = init_client()
    assert isinstance(client, genai.Client)
    # Check that client holds the vertexai and project settings
    assert client._api_client.vertexai is True

def test_stream_pdf_qa_success(sample_pdf_path):
    client = init_client()
    question = "What is the forecast GDP growth rate for 2026-27?"
    
    # Run stream and consume it
    response_chunks = list(stream_pdf_qa(client, sample_pdf_path, question))
    full_text = "".join(response_chunks)
    
    assert len(full_text) > 0
    assert "1" in full_text or "GDP" in full_text or "per cent" in full_text

def test_stream_pdf_qa_file_not_found():
    client = init_client()
    chunks = list(stream_pdf_qa(client, "non_existent_file.pdf", "Hello"))
    full_text = "".join(chunks)
    assert "Error: File not found" in full_text

def test_stream_pdf_qa_with_history(sample_pdf_path):
    client = init_client()
    history = [
        {"role": "user", "content": "What is the forecast GDP growth rate for 2026-27?"},
        {"role": "assistant", "content": "The forecast GDP growth rate for 2026-27 is 1.75 per cent."}
    ]
    question = "What about 2025-26?"
    
    chunks = list(stream_pdf_qa(client, sample_pdf_path, question, chat_history=history))
    full_text = "".join(chunks)
    
    assert len(full_text) > 0
