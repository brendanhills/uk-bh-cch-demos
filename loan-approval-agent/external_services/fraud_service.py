import time
import random
from typing import Dict, Any

from .simulation_utils import simulate_delay_async

import json
import os

# Path to the local JSON database simulating the External Fraud Detection API
DATA_FILE = os.path.join(os.path.dirname(__file__), "data/fraud_profiles.json")

async def check_fraud_risk(gov_id: str) -> Dict[str, Any]:
    """
    Simulates an external Fraud Detection API (e.g. Fraud.net).
    Returns a risk score and flags.
    """
    print(f"[ExternalAPI:FraudNet] Checking ID: {gov_id}")
    await simulate_delay_async(1) # Latency
    
    try:
        with open(DATA_FILE, "r") as f:
            risk_profiles = json.load(f)
            
        # 1. Check Specific Demo Profiles
        if gov_id in risk_profiles:
            profile = risk_profiles[gov_id]
            return {
                "provider": "Fraud.net",
                "risk_level": profile["level"],
                "risk_score": profile["score"],
                "flags": profile["flags"],
                "timestamp": time.time()
            }
            
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"[ExternalAPI:FraudNet] Warning: DB file not found or invalid at {DATA_FILE}")
        # Fallthrough to default
        
    # 2. Default Fallback (Low Risk)
    return {
        "provider": "Fraud.net",
        "risk_level": "LOW",
        "risk_score": 10,
        "flags": [],
        "timestamp": time.time()
    }
