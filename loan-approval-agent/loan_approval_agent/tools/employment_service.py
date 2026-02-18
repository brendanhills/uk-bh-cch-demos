import json
import os
import time
import random
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools import token_vault

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/external_data/employment_registry.json")

def verify_employment(applicant_id: str, company: str = None) -> Dict[str, Any]:
    """
    Verifies employment status and income.
    
    SECURITY NOTE: Receives Token ID. Internal Tool.
    """
    # DETOKENIZATION for Legacy DB Lookup
    raw_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "EMPLOYMENT_CHECK_INIT", {}, "EmploymentService")
    
    # Simulate API Latency
    time.sleep(1)
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        record = data.get(raw_id)
        
        if not record:
            log_event(applicant_id, "EMPLOYMENT_CHECK_NOT_FOUND", {}, "EmploymentService")
            return {"error": "Employment Record Not Found"}
            
        # Extract key data points for decisioning
        result = {
            "employer": record["employer"]["name"] if record["employer"] else None,
            "status": record["employment"]["status"],
            "title": record["employment"]["title"],
            "tenure_months": 24, # mocking calculation logic
            "verified_annual_income": record["employment"]["verifiedAnnualIncome"]
        }
        
        log_event(applicant_id, "EMPLOYMENT_CHECK_SUCCESS", result, "EmploymentService")
        return result

    except FileNotFoundError:
        log_event(applicant_id, "EMPLOYMENT_CHECK_ERROR", {"error": "Database missing"}, "EmploymentService")
        return {"error": "System Error: Employment Database not found"}
