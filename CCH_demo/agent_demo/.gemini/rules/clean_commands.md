# Clean Shell Commands

- **No Inline Environment Variable Prefixes**: Do NOT prepend inline environment variable overrides (e.g., `PYTHONPATH=app` or `UV_CACHE_DIR=./.uv_cache`) to shell commands when suggesting commands to the user or executing terminal tasks.
- **Prefer Project Tools & Scripts**: Use standard `uv run <command>` or project-provided helper scripts (such as `./run_demo.sh`) directly. Environment variables should be managed via `.env`, `pyproject.toml`, or project configuration files rather than inline command line prefixes.
