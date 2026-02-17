"""Intake tools for the Loan Agent."""
from typing import Dict, Optional, Any
import hashlib
import uuid
import json
import os

# Path to demo data
DEMO_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/demo_data/applicants.json")

def _get_demo_id(name: str) -> Optional[str]:
    """Look up a demo ID by name (case-insensitive)."""
    try:
        if not os.path.exists(DEMO_DATA_FILE):
            return None
            
        with open(DEMO_DATA_FILE, "r") as f:
            applicants = json.load(f)
            
        target_name = name.strip().lower()
        for app in applicants:
            if app.get("name", "").strip().lower() == target_name:
                return app.get("applicant_id")
    except Exception:
        return None
    return None


