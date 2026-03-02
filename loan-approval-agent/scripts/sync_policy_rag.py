import os
import vertexai
from vertexai.preview import rag
from loan_agent import config

# --- CONFIG ---
RAG_CORPUS_RESOURCE_NAME = "projects/uk-bh-experiments-argolis/locations/us-central1/ragCorpora/1901081992703770624"
GCS_SOURCE_URI = "gs://uk-bh-experiments-argolis-us/loan_approval_agent/confluence"

def sync_policy_to_rag():
    """
    Ingests PDF documents from GCS into the Vertex AI RAG Corpus.
    This demonstrates the automated 'Policy-as-Code' ingestion pipeline.
    """
    print(f"--- RAG Ingestion Pipeline ---")
    print(f"Source: {GCS_SOURCE_URI}")
    print(f"Target Corpus: {RAG_CORPUS_RESOURCE_NAME}")

    vertexai.init(project=config.PROJECT_ID, location="us-central1")

    try:
        # Define chunking strategy
        transformation_config = rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(
                chunk_size=512,
                chunk_overlap=100,
            ),
        )

        # Import files from GCS
        print(f"🚀 Starting ingestion from GCS...")
        # Note: Rag Engine API uses 'corpus_name'
        response = rag.import_files(
            corpus_name=RAG_CORPUS_RESOURCE_NAME,
            paths=[GCS_SOURCE_URI],
            transformation_config=transformation_config,
            max_embedding_requests_per_min=1000,
        )
        
        print(f"✅ Ingestion started successfully. (Imported: {response.imported_rag_files_count} files)")
        
        # List current files in corpus
        print("\n--- Current Corpus Files ---")
        files = rag.list_files(corpus_name=RAG_CORPUS_RESOURCE_NAME)
        for f in files:
            print(f" - {f.display_name} ({f.name})")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    sync_policy_to_rag()
