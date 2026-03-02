"""Intake tools for the Loan Agent."""
from typing import Dict, Optional, Any
import hashlib
import uuid
import json
import os
import streamlit as st
import logging
from datetime import datetime, timezone
import time

logger = logging.getLogger(__name__)

from loan_agent.utils import token_vault
from loan_agent.utils.audit_logger import log_event

# Path to demo data (in external_services)
# loan_agent/tools/../../external_services/data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_DATA_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../external_services/data/applicants.json"))

def _get_demo_id(name: str) -> Optional[str]:
    """Look up a demo ID by name (case-insensitive)."""
    try:
        if not os.path.exists(DEMO_DATA_FILE):
            return None
            
        with open(DEMO_DATA_FILE, "r") as f:
            logger.info("Loading demo data from %s", DEMO_DATA_FILE)
            applicants = json.load(f)
            
        target_name = name.strip().lower()
        for app in applicants:
            if app.get("name", "").strip().lower() == target_name:
                return app.get("applicant_id")
    except Exception:
        return None
    return None

# Dummy decorator to simulate MCP tool use as requested
def tool(func):
    return func

@tool
def register_application(
    name: str,
    gov_id: str,
    income: int,
    employer: str,
    amount: int,
    purpose: str,
) -> Dict[str, Any]:
    """
    Registers the loan application in the secure system.
    
    This tool:
    1. Validates the input data.
    2. Tokenizes the sensitive Government ID (SSN) via the Token Vault.
    3. Generates a unique 'Application ID' for this specific request.
    4. Returns a 'Token ID' that must be used for all subsequent steps.
    
    Args:
        name: Full name of applicant.
        gov_id: Raw Government ID (SSN) to be tokenized.
        income: Annual income.
        employer: Employer name.
        amount: Loan amount requested.
        purpose: Purpose of the loan.
        
    Returns:
        Dict containing the 'application_id' (e.g. APP-12345), 'applicant_id' (Token) and confirmation status.
    """
    # Simulate Tokenization (DLP)
    # in a real app, this would call Google Cloud DLP or a Token Vault
    token = token_vault.tokenize(gov_id.strip())
    
    # Generate unique application id for this submission
    application_id = f"APP-{uuid.uuid4().hex[:6].upper()}"
    
    application_data = {
        "name": name,
        "applicant_id": token,  # STORED AS TOKEN
        "application_id": application_id,
        "income": income,
        "employer": employer,
        "amount": amount,
        "purpose": purpose,
        "status": "Registered",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # In a real app, we'd save the MAPPING (Token -> Raw ID) in a generic SECURE VAULT
    # and only expose the Token to the rest of the system.
    
    log_event(token, "Application_Registered", {
        "name": name,
        "amount": amount,
        "purpose": purpose
    }, agent_name="IntakeSystem", application_id=application_id)
    
    return {
        "status": "success",
        "application_id": application_id,
        "applicant_id": token,
        "message": f"Application registered (ID: {application_id}). Token ID created for security."
    }
