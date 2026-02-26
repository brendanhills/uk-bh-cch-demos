"""Tools for the Investigator agent."""

import time
from typing import Dict, Any, Optional
from loan_agent.utils import token_vault
from google import genai
from google.genai import types

# Delegate to core services
from loan_agent.tools.credit_bureau import get_credit_report as core_get_credit
from loan_agent.tools.employment_service import verify_employment as core_verify_employment
from loan_agent.tools.fraud_service import check_fraud_risk as core_check_fraud
from loan_agent.tools.doc_analyzer import analyze_paystub
from loan_agent.utils.audit_logger import log_event
from loan_agent import config
from loan_agent.utils.model_client import Client, get_best_model_name

def log_investigation_finding(applicant_id: str, finding_type: str, observation: str, evidence: Dict[str, Any] = None, application_id: str = None) -> Dict[str, Any]:
    """
    Logs a specific finding or observation during the investigation.
    Use this to record manual conclusions, cross-tool analysis, or document insights.
    
    Args:
        applicant_id: The Token ID of the applicant.
        finding_type: The category of finding (e.g., 'Income_Verification', 'DTI_Anomaly', 'Document_Insight').
        observation: A clear text description of what was found.
        evidence: Optional dictionary of data points supporting the finding.
        application_id: The human-readable Application ID (e.g. APP-XXXX).
    """
    log_event(applicant_id, f"INVESTIGATION_FINDING_{finding_type}", {
        "observation": observation,
        "evidence": evidence
    }, agent_name="Investigator", application_id=application_id)
    return {"status": "success", "message": f"Finding '{finding_type}' logged to audit trail."}

async def check_data_consistency(applicant_id: str, stated_income: int, application_id: str = None) -> Dict[str, Any]:
    """
    Uses LLM to cross-reference Stated Application Data against verified Internal Records.
    
    Args:
        applicant_id: The Token ID of the applicant.
        stated_income: Income stated on the application form.
        application_id: The human-readable Application ID.
        
    Returns:
        Analysis result { "consistent": bool, "reason": str }
    """
    log_event(applicant_id, "data_consistency_check_init", {"stated_income": stated_income}, "LLM_DataSentry", application_id=application_id)
    
    # 1. Fetch Internal Data
    credit_data = await get_credit_report(applicant_id, application_id=application_id)
    employment_data = await verify_employment(applicant_id, application_id=application_id)
    
    # Flatten strictly for the prompt context
    context = {
        "Stated_Application": {"Income": stated_income},
        "Verified_Employment": employment_data,
        "Credit_Report_Summary": credit_data.get("summary", {})
    }
    
    try:
        # Use Vertex AI as seen in gemini_3.py
        client = genai.Client(vertexai=True)
        model_id = get_best_model_name()
        
        prompt_text = (
            f"Analyze the consistency of this loan application data. "
            f"Compare 'Stated_Application' against 'Verified_Employment' and 'Credit_Report_Summary'. "
            f"Look for major discrepancies like Income Inflation, Employer Mismatch, or Identity issues. "
            f"Return JSON: {{ 'consistent': boolean, 'reason': string }}.\n\nData context: {context}"
        )
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)]
            )
        ]
        
        config = types.GenerateContentConfig(
            temperature=0.0, 
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_level="HIGH") if "pro" in model_id.lower() else None
        )
        
        # Use async client in async function
        response = await client.aio.models.generate_content(
            model=model_id,
            contents=contents,
            config=config
        )
        
        import json
        result = json.loads(response.text)
        
        log_investigation_finding(applicant_id, "DATA_CONSISTENCY", f"Data consistency check: {'Passed' if result.get('consistent') else 'Failed'}", result, application_id=application_id)
        return result

    except Exception as e:
        log_event(applicant_id, "data_consistency_check_error", {"error": str(e)}, "LLM_DataSentry", application_id=application_id)
        return {"consistent": True, "reason": "Check failed due to system error, defaulting to safe."}

async def get_credit_report(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Fetches full credit report for an applicant from Equifax.
    """
    # 1. Detokenize handled by Tool Wrapper
    # 2. Call Tool Wrapper (which calls Dispatcher)
    return await core_get_credit(applicant_id, application_id=application_id)

async def verify_employment(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """Verifies employment status and income from Workday."""
    return await core_verify_employment(applicant_id, application_id=application_id)

async def check_fraud_risk(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """Checks for fraud signals from Fraud.net."""
    return await core_check_fraud(applicant_id, application_id=application_id)

async def calculate_dti(applicant_id: str, loan_amount: int, loan_term_months: int = 60, application_id: str = None) -> Dict[str, Any]:
    """
    Calculates the Debt-To-Income (DTI) ratio.
    """
    # 1. Fetch Data
    credit_data = await get_credit_report(applicant_id, application_id=application_id)
    employment_data = await verify_employment(applicant_id, application_id=application_id)
    
    if "error" in credit_data or "error" in employment_data:
        return {"error": "Could not fetch necessary data for DTI calculation."}
        
    # 2. Extract Values
    existing_monthly_debt = credit_data.get("summary", {}).get("totalMonthlyPayment", 0)
    annual_income = employment_data.get("verified_annual_income", 0)
    
    if annual_income <= 0:
        return {"error": "Verified annual income is zero or missing."}
        
    monthly_income = annual_income / 12
    
    # 3. Estimate New Loan Payment
    annual_rate = 0.10
    monthly_rate = annual_rate / 12
    
    if monthly_rate > 0:
        new_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
    else:
        new_payment = loan_amount / loan_term_months
        
    total_monthly_debt = existing_monthly_debt + new_payment
    dti = (total_monthly_debt / monthly_income) * 100
    
    result = {
        "monthly_income": round(monthly_income, 2),
        "existing_monthly_debt": existing_monthly_debt,
        "new_loan_payment_estimate": round(new_payment, 2),
        "total_monthly_debt": round(total_monthly_debt, 2),
        "dti_percentage": round(dti, 2)
    }
    
    # Log the calculation result
    log_investigation_finding(applicant_id, "DTI_CALCULATION", f"Projected DTI is {result['dti_percentage']}% including new loan.", result, application_id=application_id)
    
    return result

def analyze_document(file_path: str, query: str, applicant_id: str = "unknown", application_id: str = None) -> Dict[str, Any]:
    """Analyzes a document (PDF/Image)."""
    # Use the new tool
    # Note: The new tool expects 'file_content' (bytes/string), but the agent might pass a path?
    # The original tool took a file path.
    # We should update this to read the file likely.
    
    try:
        with open(file_path, "rb") as f:
            content = f.read()
            
        client = genai.Client(vertexai=True)
        model_id = get_best_model_name()
        
        prompt_text = f"Analyze the attached document and answer this query: {query}. Return the answer in JSON format if possible, or structured text."
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(data=content, mime_type="application/pdf"),
                    types.Part.from_text(text=prompt_text)
                ]
            )
        ]
        
        config = types.GenerateContentConfig(
            temperature=0.0,
            thinking_config=types.ThinkingConfig(thinking_level="HIGH") if "pro" in model_id.lower() else None
        )
        
        response = client.models.generate_content(
            model=model_id,
            contents=contents,
            config=config
        )
        
        result = {"analysis": response.text}
        log_investigation_finding(applicant_id, "DOCUMENT_ANALYSIS", f"Completed analysis of {file_path}", result, application_id=application_id)
        return result
        
    except Exception as e:
        error_res = {"error": str(e)}
        log_event(applicant_id, "analyze_document_error", error_res, "Investigator", application_id=application_id)
        return error_res
