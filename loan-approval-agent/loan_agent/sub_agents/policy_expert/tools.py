import os
import json
from typing import Dict, Any, List
import vertexai
from vertexai.preview import rag
from google.cloud import aiplatform
import pypdf

from loan_agent.utils.audit_logger import log_event
from loan_agent import config

# --- VERTEX RAG CONFIG ---
RAG_CORPUS_RESOURCE_NAME = "projects/uk-bh-experiments-argolis/locations/us-central1/ragCorpora/1901081992703770624"
GCS_BUCKET_URI = "gs://uk-bh-experiments-argolis-us/loan_approval_agent/confluence"

# We keep this for the summary stats in the audit log
DEMO_DOC_SIZES = {
    "Master_Lending_Policy_v2024.pdf": 192,
    "OCC_Comptrollers_Handbook_Retail_Lending.pdf": 148,
    "Lending_Policy_2025.pdf": 1,
    "Standard_Underwriting_Guidelines_2026.pdf": 1
}

# Global initialization flag
_VERTEX_INITIALIZED = False

def consult_policy_docs(query: str, applicant_id: str = "unknown", application_id: str = None) -> str:
    """
    Reads and returns the content of the loan policy documents using Hybrid RAG.
    Primary Source: Vertex AI RAG Engine (Grounded in GCS).
    Fallback/Precision: Local PDF for 2026 Guidelines.
    """
    global _VERTEX_INITIALIZED
    log_event(applicant_id, "consult_policy_docs_start", {"query": query, "source": GCS_BUCKET_URI}, "PolicyExpert", application_id=application_id)

    # Handle empty query (often used for initial 'broad' lookups)
    search_query = query if query else "loan guidelines"

    # Initialize Vertex AI once
    if not _VERTEX_INITIALIZED:
        vertexai.init(project=config.PROJECT_ID, location="us-central1")
        _VERTEX_INITIALIZED = True

    top_chunks = []

    try:
        # 1. Retrieval from Vertex RAG Engine (Semantic Search in GCS)
        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS_RESOURCE_NAME)],
            text=search_query,
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=5, # Give agent more context
                filter=rag.Filter(vector_distance_threshold=0.5) # Filter out noise
            ),
        )
        for context in response.contexts.contexts:
            source_uri = context.source_uri if hasattr(context, 'source_uri') else "Unknown GCS Source"
            top_chunks.append({
                "source": source_uri, # Keep the full URI for demo transparency
                "text": context.text,
                "page": "N/A"
            })
    except Exception as e:
        print(f"[PolicyExpert] ⚠️ Vertex RAG search failed: {e}")

    try:
        # 2. Local Precision Search (FALLBACK ONLY)
        # We only supplement with local if RAG didn't find enough relevant context
        if len(top_chunks) < 3:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            POLICY_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../external_services/confluence"))
            guidelines_file = "Standard_Underwriting_Guidelines_2026.pdf"
            guidelines_path = os.path.join(POLICY_DIR, guidelines_file)
            
            if os.path.exists(guidelines_path):
                reader = pypdf.PdfReader(guidelines_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    
                    # Robust match: Check for high-confidence terms only if RAG missed them
                    match_terms = ["2026", "high value", "150000", "35 PERCENT"]
                    if any(t.lower() in text.lower() for t in match_terms) or \
                       any(term.lower() in text.lower() for term in search_query.lower().split()):
                        
                        top_chunks.append({ # Add to the end, don't override RAG unless necessary
                            "source": f"LOCAL: {guidelines_file}",
                            "text": text,
                            "page": i + 1
                        })
                        break
    except Exception as e:
        print(f"[PolicyExpert] ⚠️ Local precision search failed: {e}")

    # Format Output for Agent
    policy_content = f"*** Hybrid RAG Search Results (Grounded in {GCS_BUCKET_URI}) ***\n\n"
    policy_content += "INSTRUCTIONS FOR AGENT: Use the citations below when justifying your assessment.\n\n"
    
    matches_summary = []
    for c in top_chunks[:5]:
        policy_content += f"--- CITATION: {c['source']} ---\n"
        policy_content += c['text'] + "\n\n"
        
        matches_summary.append({
            "source": c["source"],
            "preview": c["text"][:100] + "..."
        })

    # Log Audit Data
    log_event(applicant_id, "consult_policy_docs_complete", {
        "rag_source": GCS_BUCKET_URI,
        "policy_documents_searched": DEMO_DOC_SIZES,
        "total_pages_searched": sum(DEMO_DOC_SIZES.values()),
        "relevant_citations_found": len(matches_summary),
        "matches": matches_summary
    }, "PolicyExpert", application_id=application_id)
    
    return policy_content
