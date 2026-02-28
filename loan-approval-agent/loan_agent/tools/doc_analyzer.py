from typing import Dict, Any, Union
import os
from google import genai
from google.genai import types
from loan_agent import config
from loan_agent.utils.audit_logger import log_event
import base64
import json

def analyze_paystub(file_content: Union[bytes, str], applicant_id: str = "UNKNOWN", application_id: str = None) -> Dict[str, Any]:
    """
    Analyzes an uploaded paystub (image/PDF) using Gemini Vision (Multimodal).
    
    Args:
        file_content: Raw bytes of the file OR base64 string.
        applicant_id: For logging.
        
    Returns:
        Structured data: {employer, period_start, period_end, net_pay, year_to_date_income}
    """
    log_event(applicant_id, "DOC_ANALYSIS_INIT", {"type": "paystub"}, "Tool:DocAnalyzer", application_id=application_id)
    
    try:
        # 1. Instantiate Client
        client = config.get_client()
        model_id = config.MODEL_FLASH
        
        prompt_text = """
        Analyze this Paystub document.
        Extract the following fields into JSON format:
        - employer_name (str)
        - pay_period_start (str: YYYY-MM-DD)
        - pay_period_end (str: YYYY-MM-DD)
        - net_pay (float)
        - gross_pay (float)
        - year_to_date_gross (float)
        
        If you cannot find a value, return null.
        """
        
        # 2. Prepare Content
        # We need to handle the content type.
        parts = []
        if isinstance(file_content, bytes):
             # Assume image/png for now or detect?
             parts.append(types.Part.from_bytes(data=file_content, mime_type="image/png"))
        else:
             # Assume text path? Or text content?
             parts.append(types.Part.from_text(text=str(file_content)))

        parts.append(types.Part.from_text(text=prompt_text))

        contents = [
            types.Content(
                role="user",
                parts=parts
            )
        ]

        # 3. Generate
        gen_config = config.get_gen_config(is_pro=False)
        gen_config.response_mime_type = "application/json"
        
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=gen_config
        )
        
        # 4. Parse JSON
        text = response.text
        # Optional cleanup if model behaves badly despite mime_type
        if "```json" in text:
            text = text.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(text)
        
        log_event(applicant_id, "DOC_ANALYSIS_SUCCESS", data, "Tool:DocAnalyzer", application_id=application_id)
        return data

    except Exception as e:
        log_event(applicant_id, "DOC_ANALYSIS_ERROR", {"error": str(e)}, "Tool:DocAnalyzer", application_id=application_id)
        return {"error": f"Failed to analyze document: {str(e)}"}
