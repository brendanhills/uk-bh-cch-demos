"""Tools for the Investigator agent."""

import time
from typing import Dict, Any
from loan_approval_agent.tools import token_vault
from google.genai import Client
from google.genai.types import Part, UserContent, GenerateContentConfig

# Delegate to core services
from loan_approval_agent.tools.credit_bureau import get_credit_report as core_get_credit
from loan_approval_agent.tools.employment_service import verify_employment as core_verify_employment
from loan_approval_agent.tools.fraud_service import check_fraud_risk as core_check_fraud
from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent import config
from loan_approval_agent.tools.data_consistency import check_data_consistency as core_check_consistency

def get_credit_report(applicant_id: str) -> Dict[str, Any]:
    """
    Fetches full credit report for an applicant.
    
    PRIVACY NOTE: This tool runs inside the SECURE BOUNDARY.
    The agent passes a reference ID. In production, this is a distinct
    opaque token to prevents PII leakage into the model's context context.
    The tool returns abstracted risk signals, not raw data.
    """
    # 1. Detokenize to get real Gov ID (Secure Lookup)
    real_id = token_vault.detokenize(applicant_id)
    if not real_id:
        return {"error": "Invalid Token: Access Denied"}
        
    # 2. Call Core Service with Real ID
    return core_get_credit(real_id)

def verify_employment(applicant_id: str) -> Dict[str, Any]:
    """Verifies employment status and income."""
    real_id = token_vault.detokenize(applicant_id)
    if not real_id: return {"error": "Invalid Token"}
    return core_verify_employment(real_id)

def check_fraud_risk(applicant_id: str) -> Dict[str, Any]:
    """Checks for fraud signals."""
    real_id = token_vault.detokenize(applicant_id)
    if not real_id: return {"error": "Invalid Token"}
    return core_check_fraud(real_id)

def check_data_consistency(applicant_id: str, stated_income: int) -> Dict[str, Any]:
    """
    Checks for data inconsistencies (e.g. Stated Income vs Verified).
    Uses LLM to detect logic gaps.
    """
    return core_check_consistency(applicant_id, stated_income)

def analyze_document(file_path: str, query: str) -> Dict[str, Any]:
    """Analyzes a document (PDF/Image) using multimodal capabilities to answer a query."""
    log_event("system", "analyze_document_start", {"file": file_path, "query": query}, "Investigator")
    
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        client = Client()
        # Use configured model from config, fallback to flash
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
        log_event("system", "analyze_document_complete", result, "Investigator")
        return result
        
    except Exception as e:
        error_res = {"error": str(e)}
        log_event("system", "analyze_document_error", error_res, "Investigator")
        return error_res

