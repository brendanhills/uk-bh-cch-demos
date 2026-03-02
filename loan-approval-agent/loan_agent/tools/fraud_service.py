from typing import Dict, Any
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def check_fraud_risk(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Checks fraud risk via External Service.
    """
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "FRAUD_CHECK_INIT", {}, "Tool:FraudService", application_id=application_id)
    
    # Call Dispatcher
    result = await call_tool("check_fraud_risk", {"gov_id": raw_gov_id})
    print(f"[Tool:FraudService] Result for {applicant_id}: {result}")
    
    if "error" in result:
        log_event(applicant_id, "FRAUD_CHECK_ERROR", result, "Tool:FraudService", application_id=application_id)
        return result
        
    log_event(applicant_id, "FRAUD_CHECK_SUCCESS", {"risk_level": result.get("risk_level")}, "Tool:FraudService", application_id=application_id)
    return result
