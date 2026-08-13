"""Tools for document scanner auto-trigger and camera viewfinder controls (#BUG-48)."""

import logging

logger = logging.getLogger("cch_agent.document_scanner_tools")


# ==============================================================================
# DEMO ARCHITECTURE RATIONALE: Why a Tool (request_document_scan)?
#
# WHY A TOOL HERE (INSTEAD OF AN AGENT)?
# 1. Frontend Event Signal Trigger: Serves as an actionable API bridge between agent intelligence
#    and client Web UI. The WebSocket event loop intercepts this tool call function name
#    to auto-open the browser camera viewfinder.
# ==============================================================================

def request_document_scan(
    document_type: str = "discharge_summary",
    prompt_reason: str = "To inspect your child's discharge paperwork",
) -> str:
    """Triggers the client-side document scanner camera viewfinder for document snapshot capture.

    Args:
        document_type: Type of document requested (e.g. 'discharge_summary', 'prescription', 'medication_list').
        prompt_reason: Spoken or displayed explanation for why the document scan is requested.

    Returns:
        Status message confirming the camera viewfinder trigger signal was sent to the user interface.
    """
    logger.info(
        f"[REQUEST_DOCUMENT_SCAN_TOOL] Triggered document scan: document_type='{document_type}', "
        f"prompt_reason='{prompt_reason}'"
    )
    return (
        f"Camera scanner trigger dispatched to client UI for '{document_type}'. "
        f"The camera viewfinder is opening now. Please instruct the caller to align their paper in the frame and snap a photo."
    )
