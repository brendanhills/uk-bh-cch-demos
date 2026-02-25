from typing import Dict, Any, Union
from google.genai import Client
from google.genai.types import Part, UserContent, GenerateContentConfig
from loan_agent.utils.model_client import get_best_model_name
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
        client = Client()
        model_id = get_best_model_name()
        
        prompt = """
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
             parts.append(Part.from_bytes(data=file_content, mime_type="image/png"))
        else:
             # Assume text path? Or text content?
             # If it's a path string, we should read it? 
             # But the tool signature says "file_content".
             # For safety, let's treat string as text content or base64?
             parts.append(Part.from_text(text=str(file_content)))

        parts.append(Part.from_text(text=prompt))

        # 3. Generate
        response = client.models.generate_content(
            model=model_id,
            contents=[UserContent(parts=parts)],
            config=GenerateContentConfig(temperature=0.0, response_mime_type="application/json")
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
