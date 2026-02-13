# GEMINI Context: Recruiting Project

## Project Overview
This is a Python-based project named `recruiting` designed for developing agents using the `google-adk` (Agent Development Kit). The project is structured to define and manage LLM-powered agents, specifically focusing on a `candidate_feedback` module.

### Main Technologies
- **Language:** Python (>= 3.13)
- **Framework:** `google-adk` (Agent Development Kit)
- **Package Manager:** `uv`

### Architecture
- `main.py`: The primary entry point for the application (currently a placeholder).
- `candidate_feedback/`: A module containing agent definitions.
    - `agent.py`: Defines the `root_agent` using `gemini-2.5-pro` and includes tool definitions like `get_current_time`.
- `pyproject.toml`: Defines project dependencies and configuration.

## Building and Running

### Prerequisites
- [uv](https://github.com/astral-sh/uv) installed on your system.

### Setup
To install dependencies and set up the virtual environment:
```bash
uv sync
```

### Running the Application
To run the main entry point:
```bash
uv run main.py
```

### Testing
- No explicit testing framework or tests were detected. TODO: Implement unit tests for agent logic and tool implementations.

## Development Conventions
- Use `uv` for dependency management.
- Define agents and tools within the `candidate_feedback` module or similar sub-packages.
- Follow standard Python type hinting and docstring practices as seen in `candidate_feedback/agent.py`.
