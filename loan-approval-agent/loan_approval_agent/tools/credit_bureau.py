import json
import os
import time
import random
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools import token_vault

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/external_data/credit_score.json")

def get_credit_report(applicant_id: str, simulate_failure: bool = False, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves the credit report for an applicant.
    
    SECURITY NOTE: This tool operates in a Secure VPC. 
    It receives a *Unique ID* (in Production: an opaque UUID; in Demo: the Gov ID).
    The Agent does NOT receive the full Credit Report (which contains massive PII).
    Instead, this tool extracts only the specific risk signals needed for the decision.
    
    Simulates a 2-second API latency.
    """
    # DETOKENIZATION STEP (Simulated Secure Lookup)
    # The tool receives a Token, but the legacy database is keyed by Raw ID.
    raw_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "CREDIT_CHECK_INIT", {"simulate_failure": simulate_failure}, "CreditBureau", application_id=application_id)
    
    # Simulate API Latency (NFR: 2-3 seconds)
    time.sleep(2)
    
    # Simulate Random Failure (Resilience Test)
    if simulate_failure and random.random() < 0.3:
        log_event(applicant_id, "CREDIT_CHECK_FAILED", {"reason": "simulated_downtime"}, "CreditBureau", application_id=application_id)
        raise ConnectionError("Credit Bureau API is currently unavailable (Simulated).")

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        report = data.get(raw_id)
        
        if not report:
            log_event(applicant_id, "CREDIT_CHECK_NOT_FOUND", {}, "CreditBureau", application_id=application_id)
            return {"error": "Applicant not found"}
            
        log_event(applicant_id, "CREDIT_CHECK_SUCCESS", {"score": report["score"]["value"]}, "CreditBureau", application_id=application_id)
        return report

    except FileNotFoundError:
        log_event(applicant_id, "CREDIT_Check_ERROR", {"error": "Database missing"}, "CreditBureau", application_id=application_id)
        return {"error": "System Error: Credit Database not found"}
