import json
import os
import re
from datetime import datetime
from typing import Dict, Any

# Configure where logs go
# Robust absolute path resolution
base_dir = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(base_dir, "../data/audit_logs")
LOG_FILE = os.path.join(LOG_DIR, "events.jsonl")

from loan_agent.utils.dlp_guardian import guardian

def _mask_pii(data: Any) -> Any:
    """Recursively masks sensitive values using dlp_guardian."""
    if isinstance(data, dict):
        return {k: _mask_pii(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_mask_pii(item) for item in data]
    elif isinstance(data, str):
        return guardian.inspect_and_mask(data)
    else:
        return data

def log_event(applicant_id: str, event_type: str, details: Dict[str, Any], agent_name: str = "System", application_id: str = None):
    """
    Logs an event to the centralized audit trail.
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "applicant_id": applicant_id,
            "application_id": application_id,
            "event_type": event_type,
            "agent": agent_name,
            "details": _mask_pii(details),
            "dlp_enabled": bool(guardian.client)
        }

        with open(LOG_FILE, "a", buffering=1) as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())
            
    except Exception as e:
        print(f"CRITICAL: Failed to write audit log: {e}")
