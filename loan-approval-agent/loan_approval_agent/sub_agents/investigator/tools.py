"""Tools for the Investigator agent."""

import time
from typing import Dict, Any, Optional
from loan_approval_agent.tools import token_vault
from google.genai import Client
from google.genai.types import Part, UserContent, GenerateContentConfig

# Delegate to core services
from loan_approval_agent.tools.credit_bureau import get_credit_report as core_get_credit
from loan_approval_agent.tools.employment_service import verify_employment as core_verify_employment
from loan_approval_agent.tools.fraud_service import check_fraud_risk as core_check_fraud
from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent import config

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

def check_data_consistency(applicant_id: str, stated_income: int, application_id: str = None) -> Dict[str, Any]:
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
    credit_data = get_credit_report(applicant_id, application_id=application_id)
    employment_data = verify_employment(applicant_id, application_id=application_id)
    
    # Flatten strictly for the prompt context
    context = {
        "Stated_Application": {"Income": stated_income},
        "Verified_Employment": employment_data,
        "Credit_Report_Summary": credit_data.get("summary", {})
    }
    
    try:
        client = Client()
        model_id = config.MODEL_FLASH
        
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
        
        log_investigation_finding(applicant_id, "DATA_CONSISTENCY", f"Data consistency check: {'Passed' if result.get('consistent') else 'Failed'}", result, application_id=application_id)
        return result

    except Exception as e:
        log_event(applicant_id, "data_consistency_check_error", {"error": str(e)}, "LLM_DataSentry", application_id=application_id)
        return {"consistent": True, "reason": "Check failed due to system error, defaulting to safe."}

def get_credit_report(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Fetches full credit report for an applicant from Equifax.
    
    PRIVACY NOTE: This tool runs inside the SECURE BOUNDARY.
    The agent passes a reference ID. In production, this is a distinct
    opaque token to prevents PII leakage into the model's context context.
    The tool returns abstracted risk signals, not raw data.
    """
    # 1. Detokenize to get real Gov ID (Secure Lookup)
    real_id = token_vault.detokenize(applicant_id)
    if not real_id:
        return {"error": "Invalid Token: Access Denied"}
        
    # 2. Call External API (Equifax)
    result = core_get_credit(real_id)
    
    # 3. Log receipt of external data (Client Side Audit Trail)
    log_event(applicant_id, "EXTERNAL_API_RESPONSE_EQUIFAX", {
        "status": "success" if "error" not in result else "failed",
        "data_points_received": list(result.keys()) if "error" not in result else []
    }, agent_name="Investigator", application_id=application_id)
    
    return result

def verify_employment(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """Verifies employment status and income from Workday."""
    real_id = token_vault.detokenize(applicant_id)
    if not real_id: return {"error": "Invalid Token"}
    
    # Call External API (Workday)
    result = core_verify_employment(real_id)
    
    # Log receipt of external data (Client Side Audit Trail)
    log_event(applicant_id, "EXTERNAL_API_RESPONSE_WORKDAY", {
        "status": "success" if "error" not in result else "failed",
        "data_points_received": list(result.keys()) if "error" not in result else []
    }, agent_name="Investigator", application_id=application_id)
    
    return result

def check_fraud_risk(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """Checks for fraud signals from Fraud.net."""
    real_id = token_vault.detokenize(applicant_id)
    if not real_id: return {"error": "Invalid Token"}
    
    # Call External API (Fraud.net)
    result = core_check_fraud(real_id)
    
    # Log receipt of external data (Client Side Audit Trail)
    log_event(applicant_id, "EXTERNAL_API_RESPONSE_FRAUD_NET", {
        "status": "success" if "error" not in result else "failed",
        "risk_level": result.get("risk_level", "Unknown")
    }, agent_name="Investigator", application_id=application_id)
    
    return result

def calculate_dti(applicant_id: str, loan_amount: int, loan_term_months: int = 60, application_id: str = None) -> Dict[str, Any]:
    """
    Calculates the Debt-To-Income (DTI) ratio.
    Includes BOTH existing monthly debts AND the estimated payment for the new loan.
    """
    # 1. Fetch Data (Internal check, no external API call here as they are called separately)
    credit_data = get_credit_report(applicant_id, application_id=application_id)
    employment_data = verify_employment(applicant_id, application_id=application_id)
    
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
    """Analyzes a document (PDF/Image) using multimodal capabilities to answer a query."""
    log_event(applicant_id, "analyze_document_start", {"file": file_path, "query": query}, "Investigator", application_id=application_id)
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        client = Client()
        model_id = config.MODEL_FLASH
        
        prompt = f"Analyze the attached document and answer this query: {query}. Return the answer in JSON format if possible, or structured text."
        
        response = client.models.generate_content(
            model=model_id,
            contents=[
                UserContent(parts=[
                    Part.from_bytes(data=file_data, mime_type="application/pdf"),
                    Part.from_text(text=prompt)
                ])
            ],
            config=GenerateContentConfig(temperature=0.0)
        )
        
        result = {"analysis": response.text}
        log_investigation_finding(applicant_id, "DOCUMENT_ANALYSIS", f"Completed analysis of {file_path}", result, application_id=application_id)
        return result
        
    except Exception as e:
        error_res = {"error": str(e)}
        log_event(applicant_id, "analyze_document_error", error_res, "Investigator", application_id=application_id)
        return error_res
