# Strategic Production Roadmap: Enterprise Loan Agent

This document outlines the architectural evolution required to scale the Loan Approval Agent from a demo prototype to a high-throughput enterprise production system capable of processing **10,000 applications per day**.

---

## 1. High-Throughput Architecture (Google Cloud Pub/Sub)
To handle bursty loads and ensure 100% reliability, the system will transition from a synchronous request-response model to an **Event-Driven Architecture**.

### Design:
- **Ingestion**: The frontend (or API Gateway) publishes raw application data to a `loan-applications` Pub/Sub topic.
- **Worker Agents**: A fleet of ADK worker instances (running on Cloud Run or GKE) subscribe to the topic.
- **Dead-Letter Queues (DLQ)**: Failed processing attempts are routed to a DLQ for investigation or manual recovery.
- **Orchestration**: A stateful orchestrator (using Firestore or Memorystore) tracks the multi-agent progress across parallel investigation tasks.

---

## 2. Deterministic Rate Limiting
To respect external API constraints (e.g., Credit Bureau: 100 calls/minute) without dropping customer requests.

### Design:
- **Centralized Token Bucket**: Use **Google Cloud Memorystore (Redis)** to maintain a distributed token bucket.
- **Backpressure**: Worker agents check for available tokens before invoking external tools.
- **Exponential Backoff**: If tokens are exhausted, the worker utilizes the ADK's built-in retry mechanisms with jitter to queue for the next available slot.

---

## 3. Deep Historical Decisions Intelligence (Phase 2 Roadmap)
To further reduce manual oversight, the system will leverage 5 years of historical approve/deny data (18M+ records) to perform **Precedent Analysis**.

### Design:
- **Decision Warehouse**: Reasoning traces and final outcomes for all historical applications will be migrated to **BigQuery**.
- **Historical Grounding Agent**: A new specialized agent will perform semantic similarity searches across past "complex" or "escalated" cases to find how similar profiles were resolved.
- **Continuous Learning Loop**: Outcomes from BigQuery will be used to automatically retrain the ML Risk Model (v2.2.0+) every quarter.

---

## 4. Enhanced Security & Compliance
- **Model Armor**: Transition from LLM-based guardrails to Model Armor for hardened jailbreak and injection protection.
- **Audit-as-a-Service**: Stream audit logs directly to **Cloud Logging** and **BigQuery** for immutable regulatory record-keeping.
- **Data Residency**: Pin RAG corpora and processing to specific regions (e.g., `europe-west2`) to meet local regulatory requirements.
