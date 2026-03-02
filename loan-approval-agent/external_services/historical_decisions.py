import json
import os
from typing import Dict, Any, List
from .simulation_utils import simulate_delay_async

DATA_FILE = os.path.join(os.path.dirname(__file__), "data/historical_decisions.json")

async def lookup_historical_decisions(gov_id: str) -> Dict[str, Any]:
    """Simulates access to a 5-year historical decisions database."""
    await simulate_delay_async(1.5)
    
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            
        return {
            "historical_decisions": data.get(gov_id, []),
            "count": len(data.get(gov_id, []))
        }
    except Exception as e:
        return {"error": f"History Service Error: {str(e)}"}
