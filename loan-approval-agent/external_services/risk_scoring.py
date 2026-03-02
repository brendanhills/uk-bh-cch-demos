import json
import os
from typing import Dict, Any
from .simulation_utils import simulate_delay_async

DATA_FILE = os.path.join(os.path.dirname(__file__), "data/ml_risk_scores.json")

async def get_ml_risk_score(gov_id: str) -> Dict[str, Any]:
    """Simulates a custom ML model returning a risk score 0-100."""
    await simulate_delay_async(1.0)
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        if gov_id in data:
            return data[gov_id]
        
        # Default for unknown
        return {
            "risk_score": 50,
            "model_version": "v2.1.0",
            "note": "Default score for new applicant"
        }
    except Exception as e:
        return {"error": f"ML Service Error: {str(e)}"}
