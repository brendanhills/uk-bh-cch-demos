from typing import Dict, Any
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def get_ml_risk_score(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves the internal ML risk score for an applicant.
    
    Args:
        applicant_id: The Token ID of the applicant.
        application_id: The unique ID for this application.
    """
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "ML_RISK_SCORE_INIT", {}, "Tool:RiskAssessment", application_id=application_id)
    
    result = await call_tool("get_ml_risk_score", {
        "gov_id": raw_gov_id
    })
    
    if "error" in result:
        log_event(applicant_id, "ML_RISK_SCORE_FAILED", result, "Tool:RiskAssessment", application_id=application_id)
        return result

    log_event(applicant_id, "ML_RISK_SCORE_SUCCESS", {"risk_score": result.get("risk_score")}, "Tool:RiskAssessment", application_id=application_id)
    return result

async def lookup_historical_decisions(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves historical lending decisions for an applicant.
    
    Args:
        applicant_id: The Token ID of the applicant.
        application_id: The unique ID for this application.
    """
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "HISTORY_LOOKUP_INIT", {}, "Tool:RiskAssessment", application_id=application_id)
    
    result = await call_tool("lookup_historical_decisions", {
        "gov_id": raw_gov_id
    })
    
    if "error" in result:
        log_event(applicant_id, "HISTORY_LOOKUP_FAILED", result, "Tool:RiskAssessment", application_id=application_id)
        return result

    log_event(applicant_id, "HISTORY_LOOKUP_SUCCESS", {"count": result.get("count")}, "Tool:RiskAssessment", application_id=application_id)
    return result
