import os
import sys
from typing import Generator, List, Dict, Any, Optional
from google import genai
from google.genai import types

# Set necessary environment overrides for Argolis / GCP environment mTLS bypass
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS"] = "never"

# Configuration constants
DEFAULT_PROJECT = "uk-bh-experiments-argolis"
DEFAULT_LOCATION = "us-central1"
DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are an expert financial analyst assistant specializing in the Australian Federal Budget.
Your goal is to answer user queries using the provided Budget Paper No. 1 PDF document.

Strict Rules:
1. **Grounding:** ONLY answer questions based on the provided PDF document. If the answer cannot be found in the PDF or the data does not support it, respond with: "I cannot find that information in the provided budget documents." Do NOT make up any facts, and do NOT hallucinate.
2. **Citations:** Every answer you generate must show exactly where the information came from in the document. Show the filename and the exact page number(s) (e.g. `[bp1_bs-1.pdf, Page 12]`) immediately following the statement or table containing that fact.
3. **Format:** Format your response using clean, professional Markdown. Use tables for displaying comparative numeric data where helpful. Keep your tone objective, professional, and clear.
"""

def init_client(project: str = DEFAULT_PROJECT, location: str = DEFAULT_LOCATION) -> genai.Client:
    """
    Initializes and returns the Google Gen AI Client configured for Vertex AI.
    
    Args:
        project: GCP Project ID
        location: GCP region location
        
    Returns:
        genai.Client: The initialized client object.
    """
    # Force use of Vertex AI backend as required by our credentials configuration
    return genai.Client(
        vertexai=True,
        project=project,
        location=location
    )

def stream_pdf_qa(
    client: genai.Client,
    pdf_path: str,
    question: str,
    chat_history: Optional[List[Dict[str, str]]] = None,
    model: str = DEFAULT_MODEL
) -> Generator[str, None, None]:
    """
    Sends a query along with the PDF bytes to Gemini and yields chunks of the response.
    Supports chat history for multi-turn conversations.
    
    Args:
        client: The initialized genai.Client
        pdf_path: Path to the local budget PDF file
        question: The user's query/question
        chat_history: Optional list of previous chat messages formatted as:
                     [{'role': 'user'|'assistant', 'content': 'message'}]
        model: Gemini model identifier (default: gemini-2.5-flash)
        
    Yields:
        str: Incremental chunks of the text response.
    """
    if not os.path.exists(pdf_path):
        yield f"Error: File not found at {pdf_path}"
        return

    try:
        # Load PDF bytes
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
            
        # Create PDF Part
        pdf_part = types.Part.from_bytes(
            data=pdf_bytes,
            mime_type='application/pdf'
        )
        
        # Build contents array
        contents = []
        
        # We supply the PDF part. For multi-turn conversations, we prepend history
        # and attach the PDF part to the first turn to ensure grounding context.
        if chat_history:
            # Reconstruct history into types.Content structure
            for i, msg in enumerate(chat_history):
                role = "user" if msg["role"] == "user" else "model"
                # For the first user prompt, attach both PDF and text
                if i == 0 and role == "user":
                    contents.append(
                        types.Content(
                            role="user",
                            parts=[pdf_part, types.Part.from_text(text=msg["content"])]
                        )
                    )
                else:
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg["content"])]
                        )
                    )
            # Add current user turn
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=question)]
                )
            )
        else:
            # Single-turn: Send PDF part and question together
            contents = [pdf_part, question]
            
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.2, # Lower temperature for analytical grounding
        )
        
        response_stream = client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config
        )
        
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"\n\nAn error occurred while communicating with Gemini: {str(e)}"
