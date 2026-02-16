"""Mock tools for the Investigator agent."""

import random
import time
import json
import os
import asyncio
from typing import Dict, Any
from loan_approval_agent import config

# Load mock DBs
MOCK_DB_DIR = os.path.join(os.path.dirname(__file__), "../../data/mock_db")
APPLICANTS_DB_PATH = os.path.join(MOCK_DB_DIR, "applicants.json")
CREDIT_DB_PATH = os.path.join(MOCK_DB_DIR, "credit_score_db.json")

try:
    with open(APPLICANTS_DB_PATH, "r") as f:
        APPLICANTS_DB = {a["applicant_id"]: a for a in json.load(f)}
except Exception as e:
    print(f"Warning: Could not load mock DB from {APPLICANTS_DB_PATH}: {e}")
    APPLICANTS_DB = {}

try:
    with open(CREDIT_DB_PATH, "r") as f:
        # DB is now a list of objects with nested creditProfile
        raw_credit_data = json.load(f)
        CREDIT_DB = {}
        for entry in raw_credit_data:
            c_id = entry.get("creditProfile", {}).get("consumer", {}).get("id")
            if c_id:
                CREDIT_DB[c_id] = entry["creditProfile"]
except Exception as e:
    print(f"Warning: Could not load mock DB from {CREDIT_DB_PATH}: {e}")
    CREDIT_DB = {}

from loan_approval_agent.audit_logger import AuditLogger

# ... existing DB loading ...

def get_credit_report(applicant_id: str) -> Dict[str, Any]:
    """Fetches full credit report for an applicant."""
    logger = AuditLogger(applicant_id)
    logger.log_event("Investigator", "fetch_credit_report_start", {"status": "started"})
    
    # Simulate API latency (2-3s)
    time.sleep(config.get_latency(2.0, 3.0)) 
    
    result = {}
    if applicant_id in CREDIT_DB:
        profile = CREDIT_DB[applicant_id]
        summary = profile.get("summary", {})
        score = profile.get("score", {})
        
        # Calculate monthly debt obligations from tradelines
        monthly_debt = 0
        for trade in profile.get("tradelines", []):
            if trade.get("status") == "Open":
                # Use explicit monthly payment if available, else estimate min payment (e.g. 3% of balance for cards)
                payment = trade.get("monthlyPayment", 0)
                if payment == 0 and trade.get("balance", 0) > 0:
                     payment = trade.get("balance") * 0.03
                monthly_debt += payment
                
        result = {
            "applicant_id": applicant_id,
            "credit_score": score.get("value"),
            "score_factors": score.get("factors", []),
            "total_debt": summary.get("totalDebt"),
            "calculated_monthly_debt": round(monthly_debt, 2),
            "history_length": summary.get("historyLength"),
            "utilization": summary.get("creditUtilization"),
            "open_accounts": summary.get("openAccounts"),
            "derogatory_marks": summary.get("derogatoryMarks"),
            "tradelines": profile.get("tradelines", []),
            "inquiries": profile.get("inquiries", [])
        }
    else:
        result = {
            "applicant_id": applicant_id,
            "error": "Credit report not found"
        }
    
    logger.log_event("Investigator", "fetch_credit_report_complete", result)
    return result

def verify_employment(applicant_id: str) -> Dict[str, Any]:
    """Verifies employment status and income."""
    logger = AuditLogger(applicant_id)
    logger.log_event("Investigator", "verify_employment_start", {"status": "started"})

    # Simulate longer latency
    time.sleep(config.get_latency(5.0, 8.0)) 
    
    applicant = APPLICANTS_DB.get(applicant_id)
    stated_income = applicant.get("stated_income", 50000) if applicant else 50000
    # Use personal_circumstances as proxy for scenario flags if needed, or simple deterministic logic
    persona = applicant.get("persona", "") if applicant else ""
    
    seed =  sum(ord(c) for c in applicant_id)
    random.seed(seed + 1)
    
    # Deterministic salary verification
    # If persona implies instability or fraud, we simulate it
    if "variable income" in persona.lower() or "fraud" in persona.lower():
        verified_income = round(stated_income * 0.8) # 20% variance
        status = "Self-Employed / Variable"
    else:
        variance = random.uniform(0.95, 1.05)
        verified_income = round(stated_income * variance)
        status = "Active"

    result = {
        "applicant_id": applicant_id,
        "employer": "Mock Corp Inc.",
        "status": status,
        "tenure": f"{random.randint(1, 10)} years",
        "verified_annual_income": verified_income
    }
    
    logger.log_event("Investigator", "verify_employment_complete", result)
    return result

def check_fraud_risk(applicant_id: str) -> Dict[str, Any]:
    """Checks for fraud signals."""
    logger = AuditLogger(applicant_id)
    logger.log_event("Investigator", "check_fraud_risk_start", {"status": "started"})

    # Simulate API latency (1s)
    time.sleep(config.get_latency(1.0, 1.5))
    
    applicant = APPLICANTS_DB.get(applicant_id)
    persona = applicant.get("persona", "") if applicant else ""

    seed =  sum(ord(c) for c in applicant_id)
    random.seed(seed + 2)
    
    if "identity thief" in persona.lower() or "fraud" in persona.lower():
        risk_score = random.randint(85, 99)
    else:
        risk_score = random.randint(0, 20)
    
    result = {
        "applicant_id": applicant_id,
        "fraud_score": risk_score,
        "identity_verified": risk_score < 50,
        "suspicious_activity": risk_score > 80
    }
    
    logger.log_event("Investigator", "check_fraud_risk_complete", result)
    return result

from google.genai import Client
from google.genai.types import Part, UserContent, GenerateContentConfig

def analyze_document(file_path: str, query: str) -> Dict[str, Any]:
    """Analyzes a document (PDF/Image) using multimodal capabilities to answer a query."""
    logger = AuditLogger("system") # No applicant_id known yet? or pass it?
    print(f"DEBUG: analyze_document called with {file_path}")
    logger.log_event("Investigator", "analyze_document_start", {"file": file_path, "query": query})
    
    try:
        # Load file
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        client = Client()
        model_id = config.MODEL_FLASH # Use configured model
        
        prompt = f"Analyze the attached document and answer this query: {query}. Return the answer in JSON format if possible, or structured text."
        
        response = client.models.generate_content(
            model=model_id,
            contents=[
                UserContent(parts=[
                    Part.from_bytes(data=file_data, mime_type="application/pdf"),
                    Part(text=prompt)
                ])
            ],
            config=GenerateContentConfig(temperature=0.0)
        )
        
        result = {"analysis": response.text}
        logger.log_event("Investigator", "analyze_document_complete", result)
        return result
        
    except Exception as e:
        error_res = {"error": str(e)}
        logger.log_event("Investigator", "analyze_document_error", error_res)
        return error_res
        return error_res
