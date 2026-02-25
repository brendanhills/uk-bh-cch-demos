import json
import os
import time
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event
from loan_approval_agent.tools import token_vault
from loan_approval_agent.tools.simulation_utils import simulate_delay_async

# In a real system, this would be a sophisticated Fraud Detection Model
# For demo, we just return a score based on ID patterns or random

# Path to local JSON database
DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/external_data/fraud_profiles.json")

async def check_fraud_risk(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """Checks for fraud signals."""
    # DETOKENIZATION (if needed for pattern matching on Raw ID)
    raw_id = token_vault.detokenize(applicant_id) or applicant_id

    log_event(applicant_id, "FRAUD_CHECK_INIT", {}, "FraudService", application_id=application_id)

    # Simulate Processing
    await simulate_delay_async(1)

    try:
        with open(DATA_FILE, "r") as f:
            risk_profiles = json.load(f)
            
        # 1. Check Specific Demo Profiles
        if raw_id in risk_profiles:
            profile = risk_profiles[raw_id]
            result = {
                 "risk_level": profile["level"],
                 "score": profile["score"],
                 "flags": [] # Add flags to JSON if needed, or keep dynamic logic below
            }
            
            # Keep specific flags logic for now if not in JSON, or move to JSON
            if raw_id == "900-00-9999":
                 result["flags"] = ["Identity Mismatch", "Suspicious IP"]
            
            log_event(applicant_id, "FRAUD_CHECK_COMPLETE", result, "FraudService", application_id=application_id)
            return result
            
    except (FileNotFoundError, json.JSONDecodeError):
         log_event(applicant_id, "FRAUD_CHECK_ERROR", {"error": "Database missing"}, "FraudService", application_id=application_id)

    # Fallback / Default 
    result = {
        "risk_level": "Low",
        "score": 10,
        "flags": []
    }
    
    if raw_id == "000-00-0000": # missing
        result["risk_level"] = "Critical"
        result["score"] = 99
        result["flags"] = ["Invalid ID Format", "Known Bot"]
        
    log_event(applicant_id, "FRAUD_CHECK_COMPLETE", result, "FraudService", application_id=application_id)
    return result
