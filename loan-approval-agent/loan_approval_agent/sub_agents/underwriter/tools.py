from loan_approval_agent import config
from fpdf import FPDF
import os
import json
import time
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event

DECISION_DIR = os.path.join(os.path.dirname(__file__), "../../../data/decisions")

def _create_decision_pdf(record: Dict[str, Any]) -> str:
    os.makedirs(DECISION_DIR, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Loan Decision Record", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Applicant ID: {record['applicant_id']}", 0, 1)
    
    # Color code
    if "APPROVE" in record['decision'].upper():
        pdf.set_text_color(0, 150, 0)
    elif "DENY" in record['decision'].upper():
        pdf.set_text_color(150, 0, 0)
        
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Decision: {record['decision']}", 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    
    if record['interest_rate'] > 0:
        pdf.cell(0, 10, f"Approved Interest Rate: {record['interest_rate']}%", 0, 1)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reasoning:", 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, record['reason'])
    
    filename = f"decision_{record['applicant_id']}_{int(time.time())}.pdf"
    filepath = os.path.join(DECISION_DIR, filename)
    pdf.output(filepath)
    return filepath

def record_decision(applicant_id: str, decision: str, reason: str, interest_rate: float = 0.0) -> Dict[str, Any]:
    """Records the final loan decision."""
    log_event(applicant_id, "record_decision_start", {
        "decision": decision, 
        "reason": reason,
        "interest_rate": interest_rate
    }, "Underwriter")

    time.sleep(config.get_latency(0.5, 1.0))
    
    record = {
        "applicant_id": applicant_id,
        "decision": decision,
        "reason": reason,
        "interest_rate": interest_rate
    }
    
    try:
        pdf_path = _create_decision_pdf(record)
    except Exception as e:
        pdf_path = f"Error: {e}"

    print(f"\n[UNDERWRITER] Decision Recorded: {json.dumps(record, indent=2)}")
    print(f"[UNDERWRITER] Decision PDF generated at: {pdf_path}\n")
    
    result = {"status": "success", "record": record, "pdf_path": pdf_path}
    log_event(applicant_id, "record_decision_complete", result, "Underwriter")
    return result

def escalate_app(applicant_id: str, reason: str) -> Dict[str, Any]:
    """Escalates the application to a human underwriter."""
    log_event(applicant_id, "escalation_start", {"reason": reason}, "Underwriter")

    time.sleep(config.get_latency(0.3, 0.5))

    record = {
        "applicant_id": applicant_id,
        "decision": "ESCALATE",
        "reason": reason,
        "interest_rate": 0.0,
        "escalated_at": time.time()
    }
    
    try:
        pdf_path = _create_decision_pdf(record)
    except Exception as e:
        pdf_path = f"Error: {e}"

    print(f"\n[UNDERWRITER] ⚠️ ESCALATED: {json.dumps(record, indent=2)}")
    
    result = {"status": "escalated", "record": record, "ticket_id": f"TICKET-{int(time.time())}", "pdf_path": pdf_path}
    log_event(applicant_id, "escalation_complete", result, "Underwriter")
    return result
