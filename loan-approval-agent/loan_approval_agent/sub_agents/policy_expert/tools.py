import glob
import os
import pypdf

POLICY_DIR = "loan_approval_agent/data/policy_docs"

from loan_approval_agent.audit_logger import AuditLogger

def consult_policy_docs(query: str, applicant_id: str = "unknown") -> str:
    """Reads and returns the content of the loan policy documents.
    
    Args:
        query: The specific topic to look for (e.g., "credit score", "DTI").
        applicant_id: The ID of the applicant (optional, for logging).
        
    Returns:
        The content of the policy documents.
    """
    logger = AuditLogger(applicant_id)
    logger.log_event("PolicyExpert", "consult_policy_docs_start", {"query": query})

    # Base path logic
    base_path = os.path.join(os.getcwd(), POLICY_DIR)
    if not os.path.exists(base_path):
         base_path = os.path.join(os.path.dirname(__file__), "../../data/policy_docs")

    files = glob.glob(os.path.join(base_path, "*.pdf"))
    
    if not files:
        error_msg = "Error: No policy documents found."
        logger.log_event("PolicyExpert", "consult_policy_docs_error", {"error": error_msg})
        return error_msg

    # 1. Chunking
    chunks = []
    chunk_size = 1000 # characters roughly
    
    for file_path in files:
        try:
            reader = pypdf.PdfReader(file_path)
            source_name = os.path.basename(file_path)
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                # Simple page-based chunking for now
                if text.strip():
                    chunks.append({
                        "source": source_name,
                        "page": page_num + 1,
                        "text": text
                    })
        except Exception as e:
            logger.log_event("PolicyExpert", "read_error", {"file": file_path, "error": str(e)})

    # 2. Retrieval (Simple Keyword Overlap)
    if not query:
        # If no query, return first few chunks as summary
        top_chunks = chunks[:3]
    else:
        query_terms = set(query.lower().split())
        scored_chunks = []
        for chunk in chunks:
            text_lower = chunk["text"].lower()
            score = sum(1 for term in query_terms if term in text_lower)
            scored_chunks.append((score, chunk))
        
        # Sort by score desc
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        # Take top 5
        top_chunks = [c for s, c in scored_chunks[:5] if s > 0]
        
        # Fallback if no matches
        if not top_chunks:
             top_chunks = chunks[:3]

    # 3. Format Output
    policy_content = f"*** Policy Search Results for '{query}' ***\n\n"
    for c in top_chunks:
        policy_content += f"--- Source: {c['source']} (Page {c['page']}) ---\n"
        policy_content += c['text'] + "\n\n"
            
    logger.log_event("PolicyExpert", "consult_policy_docs_complete", {
        "docs_found": len(files),
        "chunks_returned": len(top_chunks)
    })
    return policy_content
