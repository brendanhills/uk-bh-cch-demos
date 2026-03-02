import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Any

# Configure where logs go
# Robust absolute path resolution
base_dir = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(base_dir, "../data/audit_logs")
LOG_FILE = os.path.join(LOG_DIR, "events.jsonl")

from loan_agent.utils.dlp_guardian import inspect_and_mask

def _mask_pii(data: Any) -> Any:
    """Recursively masks sensitive values using Cloud DLP and key-based rules."""
    SENSITIVE_KEYS = {"account_number", "ssn", "gov_id", "password", "token"}
    
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if k.lower() in SENSITIVE_KEYS:
                new_dict[k] = "*****" # Simple mask for known keys
            else:
                new_dict[k] = _mask_pii(v)
        return new_dict
    elif isinstance(data, list):
        return [_mask_pii(item) for item in data]
    elif isinstance(data, str):
        return inspect_and_mask(data)
    else:
        return data

def log_event(applicant_id: str, event_type: str, details: Dict[str, Any], agent_name: str = "System", application_id: str = "N/A"):
    """
    Logs an event to the centralized audit trail.
    
    Args:
        applicant_id: The identifier for the applicant (often a Token).
        event_type: The name of the event (e.g., 'CREDIT_CHECK_SUCCESS').
        details: Dictionary of data to log.
        agent_name: The name of the agent or tool recording the event.
        application_id: REQUIRED. The unique ID for the application. Use "N/A" if not yet created.
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Round to nearest 0.1s for readability
        now = datetime.now(timezone.utc)
        rounded_ts = now.strftime("%Y-%m-%dT%H:%M:%S") + f".{round(now.microsecond / 100000) % 10}"
        
        entry = {
            "timestamp": rounded_ts,
            "applicant_id": applicant_id,
            "application_id": application_id,
            "event_type": event_type,
            "agent": agent_name,
            "details": _mask_pii(details),
            "dlp_enabled": True # Always mandatory now
        }

        with open(LOG_FILE, "a", buffering=1) as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
            
    except Exception as e:
        print(f"CRITICAL: Failed to write audit log: {e}")
