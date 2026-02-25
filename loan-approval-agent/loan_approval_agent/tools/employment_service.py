import json
import os
import time
import random
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools import token_vault
from loan_approval_agent.tools.simulation_utils import simulate_delay_async

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/external_data/employment_registry.json")

async def verify_employment(applicant_id: str, company: str = None, application_id: str = None) -> Dict[str, Any]:
    """
    Verifies employment via the External Service.
    """
    # DETOKENIZATION for Legacy DB Lookup
    raw_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "EMPLOYMENT_CHECK_INIT", {"company": company}, "EmploymentService", application_id=application_id)
    
    # Simulate Latency (5-30s reduced for demo/test)
    # in DEMO mode this will be capped at 1.5s
    # in REALISTIC mode this will be 5-30s
    delay = random.uniform(5, 30)
    await simulate_delay_async(delay)
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        record = data.get(raw_id)
        
        if not record:
            log_event(applicant_id, "EMPLOYMENT_CHECK_NOT_FOUND", {}, "EmploymentService", application_id=application_id)
            return {"error": "Employment Record Not Found"}
            
        # Extract key data points for decisioning
        result = {
            "employer": record["employer"]["name"] if record["employer"] else None,
            "status": record["employment"]["status"],
            "title": record["employment"]["title"],
            "tenure_months": 24, # mocking calculation logic
            "verified_annual_income": record["employment"]["verifiedAnnualIncome"]
        }
        
        log_event(applicant_id, "EMPLOYMENT_CHECK_SUCCESS", result, "EmploymentService", application_id=application_id)
        return result

    except FileNotFoundError:
        log_event(applicant_id, "EMPLOYMENT_CHECK_ERROR", {"error": "Database missing"}, "EmploymentService", application_id=application_id)
        return {"error": "System Error: Employment Database not found"}
