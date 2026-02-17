import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List

class AuditLogger:
    def __init__(self, applicant_id: str):
        self.applicant_id = applicant_id
        # Sanitize ID for filename
        safe_id = "".join(c for c in applicant_id if c.isalnum() or c in ('-', '_'))
        if not safe_id: safe_id = "unknown"
        
        self.log_dir = "loan_approval_agent/data/audit_logs"
        self.log_file = os.path.join(self.log_dir, f"audit_{safe_id}.json")
        self.events: List[Dict[str, Any]] = []
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Load existing if any (to append)
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.events = data.get("events", [])
            except:
                pass

    def log_event(self, agent: str, action: str, details: Dict[str, Any]):
        """Logs a specific event to the audit trail."""
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "applicant_id": self.applicant_id,
            "agent": agent,
            "action": action,
            "details": details
        }
        self.events.append(event)
        self._flush()
        
    def _flush(self):
        """Writes current events to disk."""
        data = {
            "applicant_id": self.applicant_id,
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "event_count": len(self.events),
            "events": self.events
        }
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.events
