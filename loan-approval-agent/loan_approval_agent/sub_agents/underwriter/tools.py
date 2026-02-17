from loan_approval_agent import config
from fpdf import FPDF
import os
import json
import time
from typing import Dict, Any

DECISION_DIR = "loan_approval_agent/data/decisions"

def _create_decision_pdf(record: Dict[str, Any]) -> str:
    # ... existing pdf logic ...
    # Ensure directory exists relative to CWD
    base_path = os.path.join(os.getcwd(), DECISION_DIR)
    if not os.path.exists(os.path.dirname(base_path)):
         # Fallback to local if running from sub-dir tests
         base_path = DECISION_DIR
         
    os.makedirs(base_path, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Loan Decision Record", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Applicant ID: {record['applicant_id']}", 0, 1)
    
    # Color code decision
    if "APPROVE" in record['decision'].upper():
        pdf.set_text_color(0, 150, 0) # Green
    elif "DENY" in record['decision'].upper():
        pdf.set_text_color(150, 0, 0) # Red
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Decision: {record['decision']}", 0, 1)
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.set_font("Arial", size=12)
    
    if record['interest_rate'] > 0:
        pdf.cell(0, 10, f"Approved Interest Rate: {record['interest_rate']}%", 0, 1)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reasoning:", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, record['reason'])
    
    filename = f"decision_{record['applicant_id']}.pdf"
    filepath = os.path.join(base_path, filename)
    pdf.output(filepath)
    return filepath

from loan_approval_agent.audit_logger import AuditLogger

def record_decision(applicant_id: str, decision: str, reason: str, interest_rate: float = 0.0) -> Dict[str, Any]:
    """Records the final loan decision.
    
    Args:
        applicant_id: The unique ID of the applicant.
        decision: "APPROVE", "DENY", or "MANUAL_REVIEW".
        reason: The explanation for the decision.
        interest_rate: The approved interest rate (if approved).
        
    Returns:
        Confirmation of the recorded decision containing the PDF path.
    """
    logger = AuditLogger(applicant_id)
    logger.log_event("Underwriter", "record_decision_start", {
        "decision": decision, 
        "reason": reason,
        "interest_rate": interest_rate
    })

    # Simulate DB Write Latency
    time.sleep(config.get_latency(0.5, 1.0))
    
    record = {
        "applicant_id": applicant_id,
        "decision": decision,
        "reason": reason,
        "interest_rate": interest_rate
    }
    
    pdf_path = "Error generating PDF"
    try:
        pdf_path = _create_decision_pdf(record)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        pdf_path = f"Error: {e}"

    # In a real system, this would write to a DB.
    # For the demo, we just print to console to show the "Action"
    print(f"\n[UNDERWRITER] Decision Recorded: {json.dumps(record, indent=2)}")
    print(f"[UNDERWRITER] Decision PDF generated at: {pdf_path}\n")
    
    result = {"status": "success", "record": record, "pdf_path": pdf_path}
    logger.log_event("Underwriter", "record_decision_complete", result)
    return result

def escalate_app(applicant_id: str, reason: str) -> Dict[str, Any]:
    """Escalates the application to a human underwriter.
    
    Args:
        applicant_id: The unique ID of the applicant.
        reason: The explanation for the escalation (e.g., "Borderline credit", "Data mismatch").
        
    Returns:
        Status of the escalation.
    """
    logger = AuditLogger(applicant_id)
    logger.log_event("Underwriter", "escalation_start", {"reason": reason})

    # Simulate Latency
    time.sleep(config.get_latency(0.3, 0.5))

    record = {
        "applicant_id": applicant_id,
        "decision": "ESCALATE",
        "reason": reason,
        "interest_rate": 0.0,
        "escalated_at": time.time()
    }
    
    # We can also generate a PDF for the escalation ticket
    try:
        pdf_path = _create_decision_pdf(record)
    except Exception as e:
        pdf_path = f"Error: {e}"

    print(f"\n[UNDERWRITER] ⚠️ ESCALATED: {json.dumps(record, indent=2)}")
    
    result = {"status": "escalated", "record": record, "ticket_id": f"TICKET-{int(time.time())}", "pdf_path": pdf_path}
    logger.log_event("Underwriter", "escalation_complete", result)
    return result
