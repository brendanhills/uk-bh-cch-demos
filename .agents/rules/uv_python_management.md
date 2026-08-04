# Rule: Always Use `uv` for Python Package Management

- **Python Package Management & Execution (`uv`)**:
  - Always use `uv` commands (`uv sync`, `uv run`, `uv add`, `uv pip install`) for all Python package management, dependency installation, virtual environment creation, and script/app execution across all projects.
  - Do not use standard `pip`, `python -m venv`, or direct binary invocation when `uv` is available.
