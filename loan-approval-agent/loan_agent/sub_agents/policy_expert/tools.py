import glob
import os
import pypdf
from typing import Dict, Any

from loan_agent.utils.audit_logger import log_event

# Fix path to be relative to project root or use absolute
# loan_agent/sub_agents/policy_expert/tools.py -> ../../../../external_services/confluence
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../external_services/confluence"))

def consult_policy_docs(query: str, applicant_id: str = "unknown", application_id: str = None) -> str:
    """Reads and returns the content of the loan policy documents."""
    log_event(applicant_id, "consult_policy_docs_start", {"query": query}, "PolicyExpert", application_id=application_id)

    if not os.path.exists(POLICY_DIR):
        error_msg = f"Error: Policy directory not found at {POLICY_DIR}"
        log_event(applicant_id, "consult_policy_docs_error", {"error": error_msg}, "PolicyExpert", application_id=application_id)
        return error_msg

    files = glob.glob(os.path.join(POLICY_DIR, "*.pdf"))
    
    if not files:
        error_msg = "Error: No policy documents found."
        log_event(applicant_id, "consult_policy_docs_error", {"error": error_msg}, "PolicyExpert", application_id=application_id)
        return error_msg

    # 1. Chunking (Simplified)
    chunks = []
    for file_path in files:
        try:
            reader = pypdf.PdfReader(file_path)
            source_name = os.path.basename(file_path)
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    chunks.append({
                        "source": source_name,
                        "page": page_num + 1,
                        "text": text
                    })
        except Exception as e:
            log_event(applicant_id, "read_error", {"file": file_path, "error": str(e)}, "PolicyExpert", application_id=application_id)

    # 2. Retrieval (Simple Keyword)
    if not query:
        top_chunks = chunks[:3]
    else:
        query_terms = set(query.lower().split())
        scored_chunks = []
        priority_chunks = []
        
        for chunk in chunks:
            # Always prioritize the main policy doc
            if "Lending_Policy_2025" in chunk["source"]:
                priority_chunks.append(chunk)
                continue
                
            text_lower = chunk["text"].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            scored_chunks.append((score, chunk))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = priority_chunks + [c for s, c in scored_chunks[:5] if s > 0]
        
        # Deduplicate just in case
        seen = set()
        unique_chunks = []
        for c in top_chunks:
            signature = c["source"] + str(c["page"])
            if signature not in seen:
                seen.add(signature)
                unique_chunks.append(c)
        
        top_chunks = unique_chunks[:5]
        
        if not top_chunks:
             top_chunks = chunks[:3]

    # 3. Format Output
    policy_content = f"*** Policy Search Results for '{query}' ***\n\n"
    for c in top_chunks:
        policy_content += f"--- Source: {c['source']} (Page {c['page']}) ---\n"
        policy_content += c['text'] + "\n\n"
            
    # Prepare matches for audit log
    matches_summary = []
    for c in top_chunks:
        matches_summary.append({
            "source": c["source"],
            "preview": c["text"][:100] + "..." if len(c["text"]) > 100 else c["text"]
        })

    log_event(applicant_id, "consult_policy_docs_complete", {
        "docs_found": len(files),
        "chunks_returned": len(top_chunks),
        "matches": matches_summary
    }, "PolicyExpert", application_id=application_id)
    
    return policy_content
