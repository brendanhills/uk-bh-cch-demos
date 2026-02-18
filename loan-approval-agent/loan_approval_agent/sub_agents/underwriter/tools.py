from loan_approval_agent import config
from fpdf import FPDF
import os
import json
import time
from typing import Dict, Any

from loan_approval_agent.tools.audit_logger import log_event

DECISION_DIR = os.path.join(os.path.dirname(__file__), "../../../data/decisions")

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
    # Resolved relative to this file: ../../../data/audit_logs/events.jsonl
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "../../../data/audit_logs/events.jsonl")
    
    found_logs = False
    if os.path.exists(log_path):
        try:
            with open(log_path, "r") as f:
                # Read all lines
                lines = f.readlines()
                
                # Filter for this applicant_id or "Guest" (intake) if plausible
                # For now, strictly filter by applicant_id to avoid noise, 
                # but ALSO include "Guest" events if they are recent? 
                # Actually, strictly filtering by applicant_id is safer for "Audit Trail".
                
                app_id = record['applicant_id']
                
                # We also want to include relevant context if possible, but strict filtering is best for "Decision Record".
                # Let's simple filter.
                
                for line in lines:
                    try:
                        event = json.loads(line)
                        # Check if event relates to this applicant
                        # The 'user_id' in log_event might be the applicant_id or 'demo_user'
                        # The LOG_EVENT function signature is log_event(user_id, event_type, details, agent_name)
                        # In our code, we largely use applicant_id as user_id for logging.
                        
                        if event.get("user_id") == app_id or event.get("details", {}).get("applicant_id") == app_id:
                            found_logs = True
                            timestamp = event.get("timestamp", "")[11:19] # Time part
                            agent = event.get("agent_name", "System")
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
