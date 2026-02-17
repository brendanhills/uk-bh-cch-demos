import json
import os
import time
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event

DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/external_data/fraud_watch_list.json")

def check_fraud_risk(applicant_id: str) -> Dict[str, Any]:
    """
    Checks the applicant against fraud watchlists.
    Simulates a 0.5-second API latency.
    """
    log_event(applicant_id, "FRAUD_CHECK_INIT", {}, "FraudService")
    
    # Simulate API Latency
    time.sleep(0.5)

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        record = data.get(applicant_id)
        
        if not record:
            # If not in watchlist, assume clear (safe default)
            log_event(applicant_id, "FRAUD_CHECK_CLEAN", {"note": "No record found"}, "FraudService")
            return {"risk_level": "Low", "flags": []}
            
        # Extract risk indicators
        flags = [hit["reason"] for hit in record.get("watchlistHits", [])]
        if record["identityVerification"]["status"] != "Verified":
            flags.append("Identity Verification Failed")
            
        result = {
            "risk_level": record["riskScore"]["riskLevel"],
            "score": record["riskScore"]["value"],
            "flags": flags
        }
        
        log_event(applicant_id, "FRAUD_CHECK_COMPLETE", result, "FraudService")
        return result

    except FileNotFoundError:
        log_event(applicant_id, "FRAUD_CHECK_ERROR", {"error": "Database missing"}, "FraudService")
        return {"error": "System Error: Fraud Database not found"}
