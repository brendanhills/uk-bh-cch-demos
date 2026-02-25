from typing import Dict, Any
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def get_credit_report(applicant_id: str, simulate_failure: bool = False, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves the credit report for an applicant via the External Service.
    
    SECURITY NOTE:
    - This tool runs inside the Secure Agent Boundary.
    - It receives a Token ID.
    - It MUST detokenize to get the Gov ID before calling the external API.
    - It MUST re-tokenize or filter the response before passing it back to the LLM (if raw PII is returned).
    """
    
    # 1. Detokenize to get Gov ID (e.g. "900-00-1234") from Token (e.g. "TOKEN-123")
    # For the demo, we often use the Gov ID directly, so we handle both.
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
