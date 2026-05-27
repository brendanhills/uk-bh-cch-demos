# MVP Implementation Plan: Distributed Agent Platform

## Background & Motivation
CSIRO requires a multi-faceted AI platform leveraging Google's ADK (Agentic Development Kit). The platform needs to support specialized agents, ensure security policy adherence, provide an enterprise gateway, and include content moderation (Model Armor). A distributed microservices architecture has been selected to allow for independent scaling and realistic "Agent Onboarding" scenarios.

## Scope & Impact
*   **Enterprise Portal:** A central FastAPI/ADK application acting as the primary interface. It will route requests to specialized agents and implement the "Model Armor" middleware.
*   **Security Agent:** An independent ADK service that analyzes GitHub commits/changes against a defined security policy.
*   **Geopolitical Agent:** An independent ADK service connected to mock geopolitical data sources, simulating a researcher-created agent.

## Proposed Solution (Architecture)
*   **Framework:** Python 3.13+, `google-adk`, `fastapi`, `uvicorn`.
*   **Dependency Management:** `uv` will be strictly used for all package management and environment isolation.
*   **Communication:** ADK's A2A (Agent-to-Agent) protocol or standard REST APIs for cross-agent communication.
*   **Model Armor:** Implemented as an interceptor/middleware in the Enterprise Portal that redacts specific PII or unapproved keywords before passing the prompt to the sub-agent and after receiving the response.

## Implementation Steps

### Phase 1: Foundation & Enterprise Portal
1.  Initialize the workspace structure (`/enterprise-portal`, `/agents/security-agent`, `/agents/geo-agent`).
2.  Set up the Python environment with `uv` and install `google-adk`, `fastapi`, and dependencies.
3.  Develop the **Enterprise Portal** skeleton.
4.  Implement the **Model Armor** component (e.g., simple regex or an LLM-based redaction step).

### Phase 2: Specialized Agents
1.  Develop the **Security Agent**:
    *   Create a mock GitHub integration tool to fetch diffs.
    *   Define a mock security policy document.
    *   Prompt the agent to evaluate diffs against the policy.
2.  Develop the **Geopolitical Agent**:
    *   Create mock tools to query "GE" data.
    *   Configure the agent to handle geopolitical queries.

### Phase 3: Integration & UI
1.  Configure the Enterprise Portal to communicate with the Security and Geopolitical agents using ADK's remote invocation patterns.
2.  Use `adk web` or build a simple web dashboard served by the Enterprise Portal to interact with the system.

### Phase 4: Deployment Preparation
1.  Create `Dockerfile`s for each component (Portal, Security, Geo) compliant with Google Cloud Run requirements (port 8080, etc.).

## Verification
*   Test that the Security Agent correctly identifies policy violations in mock commits.
*   Test that the Model Armor correctly redacts sensitive keywords from prompts/responses.
*   Test that the Enterprise Portal correctly routes queries to the appropriate specialized agent based on context.

## Alternatives Considered
*   **Unified Monolith:** Rejected in favor of a distributed architecture to better simulate the "Agent Onboarding" requirement where IM&T hosts disparate agent models.