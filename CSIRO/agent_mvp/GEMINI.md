# Project Instructions

## Dependency Management
- **Tool:** Always use `uv` for dependency management.
- **Workflow:**
  - Use `uv init` to initialize new Python projects/packages.
  - Use `uv add <package>` to add dependencies.
  - Use `uv run <command>` or `uv sync` to manage environments.
  - Use `uv lock` to maintain lockfiles.
  - Do NOT use `pip` directly unless `uv` is unavailable or specifically requested otherwise.
