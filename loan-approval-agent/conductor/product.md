# Product Guide: Loan Approval Agent (Interview Demo)

## Core Vision
A high-impact demonstration of agentic AI capabilities, specifically engineered for a 10-minute technical presentation. This system showcases how the Google Cloud Agent Development Kit (ADK) can orchestrate a complex, regulated workflow (loan underwriting) by transforming static policy documents and disconnected APIs into a cohesive, intelligent, and transparent decision-making engine.

## Primary Objectives
- **Strategic Demonstration**: Clearly articulate the value of agentic "orchestration" over simple linear automation.
- **Architectural Storytelling**: Use a 10-minute window to convey complex technical concepts (Multi-Agent systems, RAG, and Human-in-the-Loop) through a compelling, real-world narrative.
- **Business Impact**: Show how AI can solve the "48-hour bottleneck" (identified in the interview task) while maintaining 100% auditability and compliance.

## Target Audience
- **Interview Panel**: Technical and non-technical stakeholders evaluating proficiency in Generative AI architecture and the ability to simplify complex system designs.

## Key Demo Features (Optimized for 10 Minutes)
1. **Interactive Intake**: Rapid data capture that highlights the agent's ability to extract structured information from natural conversation.
2. **Parallel Investigation**: A visual "trace" of the agent calling Credit, Employment, and Fraud services simultaneously, demonstrating efficiency.
3. **Policy Expert RAG**: A live look-up where the agent cites specific policy PDF guidelines to justify a decision, showcasing grounding and accuracy.
4. **Decision Synthesis & HIL**: The Underwriter Agent's final reasoning chain, culminating in either a "Fast-Path" approval or a seamless escalation to a human for complex cases.
5. **Transparency & Trust**: Automated generation of a Decision PDF and live Audit Logs to prove regulatory compliance.

## Demo Persona & Narrative
- **The Problem**: 48-hour approval delay causing customer churn.
- **The Solution**: An agentic system that auto-approves 70% of cases in under 5 minutes.
- **The Proof**: A live walkthrough of a "Straightforward" case vs. a "Complex" case.

## Architecture Overview

The system is designed with a modular architecture to ensure security (DLP), clear separation of concerns, and realistic simulation of external dependencies.

### 1. external_services/
Simulates the "outside world" (untrusted boundary).
- **Simulators**: Mock implementations of Credit Bureaus, Employment Registries, and Fraud Services.
- **Data**: Source truth for applicants and loan scenarios.

### 2. loan_agent/
The core "Intelligent Core" built with Google Cloud ADK.
- **Loan Manager**: Root orchestrator managing the workflow.
- **Investigator Agent**: Gathers multi-source data using parallel tool execution.
- **Policy Expert Agent**: Performs keyword-based RAG against a 300+ page PDF corpus.
- **Underwriter Agent**: Synthesizes all findings into a final, compliant decision.
- **Security & Audit**: DLP Guardian for PII redaction and an encrypted-simulation Token Vault for identity protection.

### 3. demo_frontend/
Interactive Streamlit dashboard.
- **User Portal**: Corporate-style chat interface for loan applications.
- **Audit Trace**: A live, high-transparency view of the agent's internal reasoning and tool calls.
- **Compliance Records**: Automated generation and download of decision artifacts.
