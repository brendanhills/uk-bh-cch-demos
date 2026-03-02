from typing import Dict, Any
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def get_credit_report(applicant_id: str, simulate_failure: bool = False, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves the credit report for an applicant via the External Service.
    """
    # Detect if we should simulate failure from the input context/instruction
    # (In the ADK, we can pass this through arguments or detected from system instructions)
    
    # Detokenize to get Gov ID
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    log_event(applicant_id, "CREDIT_CHECK_INIT", {}, "Tool:CreditBureau", application_id=application_id)
    
    # 2. Call External Service via Dispatcher (MCP-Lite)
    result = await call_tool("get_credit_report", {
        "gov_id": raw_gov_id,
        "simulate_failure": simulate_failure
    })
    
    if "error" in result:
        log_event(applicant_id, "CREDIT_CHECK_FAILED", result, "Tool:CreditBureau", application_id=application_id)
        if "simulated" in str(result.get("error", "")).lower():
             raise ConnectionError("Credit Bureau API is currently unavailable (Simulated).")
        return result

    # 3. Security Filter: Ensure we don't leak raw PII unnecessarily?
    # For now, we trust the External Service to return only the "report" data.
    
    log_event(applicant_id, "CREDIT_CHECK_SUCCESS", {"score": result.get("score")}, "Tool:CreditBureau", application_id=application_id)
    return result
