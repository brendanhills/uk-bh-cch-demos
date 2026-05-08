# Project Instructions

## Python Package Management
- Always use `uv` instead of `pip` for managing dependencies and running scripts.
- **Rule:** Never use `PYTHONPATH=.`. Modules must be discoverable via standard package structure and configuration.
- Example: `uv run scripts/orchestrate_data_generation.py`

## Agent Definitions
- **Rule:** Whenever defining an agent, explicitly state the execution environment (e.g., "Google Enterprise Agent Designer", "Google ADK (Python)", etc.).
- **Technical Capability:** Python and standard data libraries (pandas, matplotlib, etc.) ARE permitted in agents with "coding" or "analytical" capabilities in the Agent Designer environment.
- This ensures clarity on available features (like `Knowledge` or `Personalization`) and technical constraints.
