# CSIRO TDA - Federated Agentic Architecture MVP Support

This project provides the synthetic data and prompt engineering artifacts to support the **CSIRO Technical Design Authority (TDA) Agent MVP**, demonstrating a federated multi-agent architecture in the **Google Enterprise Agent Designer**.

## **Project Scope**
1.  **High-Fidelity Synthetic Data:** Generation of localized (Australian) cloud supplier documents (AWS, Azure, Google Cloud) and security policies to act as the "Static Truth" for SME agents.
2.  **Modular Prompt Engineering:** Optimized system prompts for a federated agent team (Root, Billing, Contract, FinOps, Data Science, and Security) following the **Google Enterprise Agent Designer** environment constraints.

## **Quick Start**
- **Requirements:** Python 3.13+, `uv` package manager.
- **Generate Data:** `uv run scripts/orchestrate_data_generation.py`
- **Output:** Synthetic documents in `synthetic_data/cloud_finops/`.
- **Prompts:** Final agent instructions in `agents/cloud_agent/`.

## **Demonstration**
A set of 10 validated demonstration questions is available in `agents/cloud_agent/demo_questions.md` to showcase orchestration, grounding, and governance.

## **Execution Environment**
All agents are designed to run in the **Google Enterprise Agent Designer**. Coding-capable agents (like the Data Science Sub-agent) are explicitly permitted to use **Python** for deterministic analysis.
