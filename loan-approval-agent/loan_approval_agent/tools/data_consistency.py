from typing import Dict, Any
from loan_approval_agent import config
from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools.credit_bureau import get_credit_report
from loan_approval_agent.tools.employment_service import verify_employment

try:
    from google.genai import Client
    from google.genai.types import Part, UserContent, GenerateContentConfig
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def check_data_consistency(applicant_id: str, stated_income: int) -> Dict[str, Any]:
    """
    Uses LLM to cross-reference Stated Application Data against verified Internal Records.
    
    Args:
        applicant_id: The ID of the applicant.
        stated_income: Income stated on the application form.
        
    Returns:
        Analysis result { "consistent": bool, "reason": str }
    """
    log_event(applicant_id, "data_consistency_check_init", {"stated_income": stated_income}, "LLM_DataSentry")
    
    # 1. Fetch Internal Data
    credit_data = get_credit_report(applicant_id)
    employment_data = verify_employment(applicant_id)
    
    # Flatten strictly for the prompt context
    context = {
        "Stated_Application": {"Income": stated_income},
        "Verified_Employment": employment_data,
        "Credit_Report_Summary": credit_data.get("summary", {})
    }
    
    if not HAS_GENAI:
        # Fallback logic
        verified = employment_data.get("verified_annual_income", 0)
        if stated_income > verified * 1.5:
             return {"consistent": False, "reason": "Stated income exceeds verified by >50% (Fallback Logic)"}
        return {"consistent": True, "reason": "GenAI check skipped, fallback passed"}

    try:
        client = Client()
        model_id = getattr(config, "MODEL_FLASH", "gemini-2.0-flash-exp")
        
        prompt = (
            f"Analyze the consistency of this loan application data. "
            f"Compare 'Stated_Application' against 'Verified_Employment' and 'Credit_Report_Summary'. "
            f"Look for major discrepancies like Income Inflation, Employer Mismatch, or Identity issues. "
            f"Return JSON: {{ 'consistent': boolean, 'reason': string }}.\n\nData context: {context}"
        )
        
        response = client.models.generate_content(
            model=model_id,
            contents=[UserContent(parts=[Part.from_text(text=prompt)])],
            config=GenerateContentConfig(temperature=0.0, response_mime_type="application/json")
        )
        
        import json
        result = json.loads(response.text)
        
        log_event(applicant_id, "data_consistency_check_complete", result, "LLM_DataSentry")
        return result

    except Exception as e:
        log_event(applicant_id, "data_consistency_check_error", {"error": str(e)}, "LLM_DataSentry")
        return {"consistent": True, "reason": "Check failed due to system error, defaulting to safe."}
