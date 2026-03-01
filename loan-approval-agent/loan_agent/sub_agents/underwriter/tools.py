from loan_agent import config
from fpdf import FPDF
import os
import json
import time
from typing import Dict, Any

from loan_agent.utils.audit_logger import log_event

# Paths relative to this file: loan_agent/sub_agents/underwriter/tools.py
base_dir = os.path.dirname(os.path.abspath(__file__))
# loan_agent/sub_agents/underwriter/tools.py -> ../../data/decisions
DECISION_DIR = os.path.abspath(os.path.join(base_dir, "../../data/decisions"))

def _create_decision_pdf(record: Dict[str, Any]) -> str:
    # Ensure directory exists
    if not os.path.exists(DECISION_DIR):
        os.makedirs(DECISION_DIR)
    
    pdf = FPDF()
    pdf.add_page()
    
    # --- Header ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Loan Decision Record", 0, 1, 'C')
    pdf.ln(5)
    
    # --- Applicant Info ---
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Applicant ID: {record['applicant_id']}", 0, 1)
    if record.get('application_id'):
        pdf.cell(0, 10, f"Application ID: {record['application_id']}", 0, 1)
    pdf.cell(0, 10, f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.ln(5)
    
    # --- Decision Section ---
    pdf.set_font("Arial", 'B', 14)
    # Color code
    decision_text = record['decision'].upper()
    if "APPROVE" in decision_text:
        pdf.set_text_color(0, 128, 0) # Green
    elif "DENY" in decision_text:
        pdf.set_text_color(180, 0, 0) # Red
    elif "ESCALATE" in decision_text:
        pdf.set_text_color(200, 120, 0) # Orange
        
    pdf.cell(0, 10, f"Decision: {decision_text}", 0, 1)
    pdf.set_text_color(0, 0, 0) # Reset
    
    pdf.set_font("Arial", size=12)
    if record.get('interest_rate', 0) > 0:
        pdf.cell(0, 10, f"Approved Interest Rate: {record['interest_rate']}%", 0, 1)
        
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reasoning:", 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 6, record['reason'])
    pdf.ln(10)
    
    # --- Audit Log Section ---
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Audit Trail / Reasoning Trace", 0, 1)
    pdf.set_font("Arial", size=8)  # Smaller font for logs
    
    # Path to Audit Log
    # loan_agent/sub_agents/underwriter/tools.py -> ../../data/audit_logs/events.jsonl
    log_path = os.path.abspath(os.path.join(base_dir, "../../data/audit_logs/events.jsonl"))
    
    found_logs = False
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                # Read all lines
                lines = f.readlines()
                
                app_id = record['applicant_id']
                from loan_agent.utils import token_vault
                raw_id = token_vault.detokenize(app_id)
                
                # Specific filtering criteria for this PDF
                target_app_id = record.get('application_id')
                target_applicant_id = record.get('applicant_id')
                
                for line in lines:
                    try:
                        event = json.loads(line)
                        log_app_id = event.get("application_id")
                        log_applicant_id = event.get("applicant_id")
                        
                        # Match: Must match application_id if we have one, otherwise fall back to applicant_id
                        is_match = False
                        if target_app_id and target_app_id != "N/A":
                            is_match = (log_app_id == target_app_id)
                        else:
                            is_match = (log_applicant_id == target_applicant_id)
                        
                        if is_match:
                            found_logs = True
                            timestamp = event.get("timestamp", "")[11:19] # Time part
                            agent = event.get("agent", "System")
                            evt_type = event.get("event_type", "Unknown")
                            
                            # Format: [Time] [Agent] Event: Details
                            log_str = f"[{timestamp}] [{agent}] {evt_type}"
                            pdf.set_font("Courier", 'B', 8)
                            pdf.cell(0, 5, log_str, 0, 1)
                            
                            # Details
                            details = event.get("details", {})
                            # Convert details to string, maybe pretty print if short
                            detail_str = json.dumps(details)
                            pdf.set_font("Courier", size=8)
                            pdf.multi_cell(0, 4, detail_str)
                            pdf.ln(2)
                            
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            pdf.cell(0, 5, f"Error reading logs: {str(e)}", 0, 1)
    
    if not found_logs:
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 10, "(No audit logs found for this ID)", 0, 1)

    # Filename format: decision_APP-ID_timestamp.pdf or decision_user-ID_timestamp.pdf
    id_for_file = record.get('application_id') or record['applicant_id']
    filename = f"decision_{id_for_file}_{int(time.time())}.pdf"
    filepath = os.path.join(DECISION_DIR, filename)
    pdf.output(filepath)
    return filepath

def record_decision(applicant_id: str, decision: str, reason: str, interest_rate: float = 0.0, application_id: str = None) -> Dict[str, Any]:
    """Records the final loan decision."""
    log_event(applicant_id, "record_decision_start", {
        "decision": decision, 
        "reason": reason,
        "interest_rate": interest_rate,
        "application_id": application_id
    }, "Underwriter", application_id=application_id)

    # Simulate Latency if needed, but this is an output tool.
    # We can use the centralized latency config or just keep it minimal.
    # The original had time.sleep, let's keep it but check config?
    # Actually, let's allow it to be fast.
    
    record = {
        "applicant_id": applicant_id,
        "application_id": application_id,
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
    log_event(applicant_id, "record_decision_complete", result, "Underwriter", application_id=application_id)
    return result

def escalate_app(applicant_id: str, reason: str, application_id: str = None) -> Dict[str, Any]:
    """Escalates the application to a human underwriter."""
    log_event(applicant_id, "escalation_start", {"reason": reason, "application_id": application_id}, "Underwriter", application_id=application_id)

    record = {
        "applicant_id": applicant_id,
        "application_id": application_id,
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
    log_event(applicant_id, "escalation_complete", result, "Underwriter", application_id=application_id)
    return result
