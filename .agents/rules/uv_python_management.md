# Rule: Always Use `uv` for Python Execution & Package Management

- **Python Execution & Environment Management (`uv`)**:
  - Always use `uv run <command>` (e.g. `uv run python script.py`, `uv run streamlit run app.py`) to execute all Python scripts, binaries, and applications.
  - Always use `uv` commands (`uv add`, `uv sync`, `uv pip install`) for installing dependencies and managing virtual environments.
  - Do NOT invoke raw `python3`, `pip`, or `python -m venv` directly when `uv` is available.
