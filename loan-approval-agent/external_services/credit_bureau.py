import json
import os
import time
import random
from typing import Dict, Any

from .simulation_utils import simulate_delay_async

# Path to the local JSON database simulating the External Credit Bureau's data
DATA_FILE = os.path.join(os.path.dirname(__file__), "data/credit_score.json")

async def get_credit_report(gov_id: str, simulate_failure: bool = False) -> Dict[str, Any]:
    """
    Simulates an external Credit Bureau API Check.
    
    Args:
        gov_id: The Government ID (SSN) of the applicant.
        simulate_failure: If True, may raise an error to test resilience.
        
    Returns:
        Dict: The full credit report or error message.
    """
    print(f"[ExternalAPI:CreditBureau] Received request for ID: {gov_id}")
    
    # Simulate API Latency (2 seconds)
    # Simulate API Latency (2 seconds)
    await simulate_delay_async(2)
    
    # Simulate Random Failure
    if simulate_failure and random.random() < 0.3:
        print("[ExternalAPI:CreditBureau] Simulated 503 Service Unavailable")
        raise ConnectionError("Credit Bureau API is currently unavailable (Simulated).")

    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        # The JSON is keyed by Gov ID ("900-00-1234")
        report = data.get(gov_id)
        
        if not report:
            print(f"[ExternalAPI:CreditBureau] ID {gov_id} NOT FOUND")
            return {"error": "Applicant not found in Credit Bureau"}
            
        print(f"[ExternalAPI:CreditBureau] Success. Score: {report.get('score', {}).get('value')}")
        return report

    except FileNotFoundError:
        print("[ExternalAPI:CreditBureau] CRITICAL: DB File Missing")
        return {"error": "System Error: Credit Database not found"}
