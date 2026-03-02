from typing import Dict, Any
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def verify_employment(applicant_id: str, company: str = None, application_id: str = None) -> Dict[str, Any]:
    """
    Verifies employment via the External Service.
    """
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "EMPLOYMENT_CHECK_INIT", {"company": company}, "Tool:EmploymentService", application_id=application_id)
    
    # Call Dispatcher
    result = await call_tool("verify_employment", {
        "gov_id": raw_gov_id,
        "company": company
    })
    
    if "error" in result:
        log_event(applicant_id, "EMPLOYMENT_CHECK_NOT_FOUND", result, "Tool:EmploymentService", application_id=application_id)
        return result
        
    log_event(applicant_id, "EMPLOYMENT_CHECK_SUCCESS", {"employer": result.get("employer")}, "Tool:EmploymentService", application_id=application_id)
    return result
