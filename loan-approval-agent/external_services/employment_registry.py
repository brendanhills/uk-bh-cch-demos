import json
import os
import time
from typing import Dict, Any

from .simulation_utils import simulate_delay_async

# Path to local JSON database
DATA_FILE = os.path.join(os.path.dirname(__file__), "data/employment_registry.json")

async def verify_employment(gov_id: str, company: str = None) -> Dict[str, Any]:
    """
    Simulates an external Employment Verification API (e.g., Workday/The Work Number).
    """
    print(f"[ExternalAPI:EmploymentRegistry] Verifying ID: {gov_id}")
    
    # Simulate Latency
    import random
    delay = random.uniform(5, 30)
    await simulate_delay_async(delay)
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        record = data.get(gov_id)
        
        if not record:
            print(f"[ExternalAPI:EmploymentRegistry] ID {gov_id} NOT FOUND")
            return {"error": "Employment Record Not Found"}
            
        # Extract key data points for the caller
        result = {
            "employer": record.get("employer", {}).get("name"),
            "status": record.get("employment", {}).get("status"),
            "title": record.get("employment", {}).get("title"),
            "tenure_months": 24, # mocking calculation
            "verified_annual_income": record.get("employment", {}).get("verifiedAnnualIncome")
        }
        
        print(f"[ExternalAPI:EmploymentRegistry] Success. Employer: {result['employer']}")
        return result

    except FileNotFoundError:
        return {"error": "System Error: Employment Database not found"}
