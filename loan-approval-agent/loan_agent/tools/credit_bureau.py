from typing import Dict, Any
import asyncio
import time
from loan_agent.utils.tool_dispatcher import call_tool
from loan_agent.utils.audit_logger import log_event
from loan_agent.utils import token_vault

async def get_credit_report(applicant_id: str, application_id: str = None) -> Dict[str, Any]:
    """
    Retrieves the credit report for an applicant with exponential backoff retry logic.
    """
    raw_gov_id = token_vault.detokenize(applicant_id) or applicant_id
    
    max_retries = 5
    base_delay = 1.0 # seconds
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            log_event(applicant_id, "CREDIT_CHECK_ATTEMPT", {"attempt": attempt + 1}, "Tool:CreditBureau", application_id=application_id)
            
            # Call External Service via Dispatcher
            result = await call_tool("get_credit_report", {
                "gov_id": raw_gov_id
            })
            
            if "error" in result:
                # If it's a simulated downtime, we log and retry
                if "unavailable" in str(result.get("error", "")).lower():
                    log_event(applicant_id, "CREDIT_CHECK_RETRYING", {"reason": result["error"], "next_retry_in": base_delay * (2 ** attempt)}, "Tool:CreditBureau", application_id=application_id)
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    last_error = result
                    continue
                else:
                    # Other errors (e.g. ID not found) should fail immediately
                    log_event(applicant_id, "CREDIT_CHECK_FAILED", result, "Tool:CreditBureau", application_id=application_id)
                    return result

            # Success path
            log_event(applicant_id, "CREDIT_CHECK_SUCCESS", {"score": result.get("score")}, "Tool:CreditBureau", application_id=application_id)
            return result

        except Exception as e:
            log_event(applicant_id, "CREDIT_CHECK_EXCEPTION", {"error": str(e)}, "Tool:CreditBureau", application_id=application_id)
            await asyncio.sleep(base_delay * (2 ** attempt))
            last_error = {"error": str(e)}

    # If we reached here, we exhausted retries
    return last_error or {"error": "Maximum retries exceeded for Credit Bureau check."}
