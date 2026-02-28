import glob
import os
import pypdf
from typing import Dict, Any

from loan_agent.utils.audit_logger import log_event

# Fix path to be relative to project root or use absolute
# loan_agent/sub_agents/policy_expert/tools.py -> ../../../../external_services/confluence
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POLICY_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../external_services/confluence"))

# Global cache for policy chunks to speed up demo
_POLICY_CHUNKS_CACHE = []

def consult_policy_docs(query: str, applicant_id: str = "unknown", application_id: str = None) -> str:
    """Reads and returns the content of the loan policy documents."""
    global _POLICY_CHUNKS_CACHE
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

    # 1. Loading/Chunking (with Cache)
    if not _POLICY_CHUNKS_CACHE:
        print("[PolicyExpert] 📄 Parsing policy PDFs for the first time (caching)...")
        
        for file_path in files:
            try:
                reader = pypdf.PdfReader(file_path)
                source_name = os.path.basename(file_path)
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        _POLICY_CHUNKS_CACHE.append({
                            "source": source_name,
                            "page": page_num + 1,
                            "text": text
                        })
            except Exception as e:
                log_event(applicant_id, "read_error", {"file": file_path, "error": str(e)}, "PolicyExpert", application_id=application_id)
    
    chunks = _POLICY_CHUNKS_CACHE

    # 2. Retrieval (Simple Keyword)
    if not query:
        top_chunks = chunks[:3]
    else:
        query_terms = set(query.lower().split())
        scored_chunks = []
        
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            
            # --- RAG SCORING LOGIC ---
            # We use a simple keyword-based scoring with weighted 'Boosters' and 'Penalties'
            # to ensure the most relevant policies are prioritized.
            
            # BOOSTER: Significant weight for the primary policy documents (2026 Guidelines)
            if "Standard_Underwriting_Guidelines_2026" in chunk["source"]:
                score += 20
            elif "Lending_Policy_2025" in chunk["source"]:
                score += 10
                
            # PENALTY: Reduce noise from the massive OCC handbook (140+ pages) 
            # unless the keyword match is extremely strong.
            if "OCC_Comptrollers_Handbook" in chunk["source"]:
                score -= 5
                
            if score > 0:
                scored_chunks.append((score, chunk))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [c for s, c in scored_chunks[:5]]
        
        # Deduplicate and ensure we always include the first page of 2026 Guidelines if it's not there
        if not any("Standard_Underwriting_Guidelines_2026" in c["source"] for c in top_chunks):
            for c in chunks:
                if "Standard_Underwriting_Guidelines_2026" in c["source"]:
                    top_chunks.insert(0, c)
                    break
        
        top_chunks = top_chunks[:5]

    # 3. Format Output
    policy_content = f"*** Policy Search Results for '{query}' ***\n\n"
    policy_content += "INSTRUCTIONS FOR AGENT: Use the citations below (Source and Page) when justifying your assessment.\n\n"
    for c in top_chunks:
        policy_content += f"--- CITATION: {c['source']} (Page {c['page']}) ---\n"
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
