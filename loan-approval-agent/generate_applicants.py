"""Generates synthetic applicant data for the Loan Approval Demo."""

import json
import random
import uuid

def generate_applicants():
    applicants = []
    
    # Scenarios to ensure we cover
    scenarios = [
        ("High Credit, Low DTI", "APPROVE"),
        ("Low Credit", "DENY"),
        ("High DTI", "DENY"),
        ("Borderline - High Income", "MANUAL_REVIEW"),
        ("Fraud Risk", "DENY"),
        ("Perfect Candidate", "APPROVE"),
        ("Young History", "MANUAL_REVIEW")
    ]
    
    for _ in range(3): # Generate 3 batches of scenarios
        for scenario_name, expected_outcome in scenarios:
            applicant = {
                "applicant_id": str(uuid.uuid4())[:8],
                "name": f"Mock Applicant {random.randint(1000, 9999)}",
                "scenario": scenario_name,
                "expected_outcome": expected_outcome,
                # These fields would normally come from the initial application
                "stated_income": random.randint(30000, 150000),
                "requested_amount": random.randint(5000, 50000)
            }
            applicants.append(applicant)
            
    # Write to a JSON file that the frontend/demo script can load
    with open("loan_approval_agent/data/mock_db/applicants.json", "w") as f:
        json.dump(applicants, f, indent=2)
        
    print(f"Generated {len(applicants)} applicants in loan_approval_agent/data/mock_db/applicants.json")

if __name__ == "__main__":
    generate_applicants()
