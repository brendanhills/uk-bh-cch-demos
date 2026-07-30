# Agent Safety Boundaries & Operational Standards

## 1. Global Guardrail Protection (Modifying AGENTS.md)
The agent core engine enforces strict, hardcoded system protection boundaries on configuration files that dictate agent behavior and constraints (most notably, `~/.gemini/config/AGENTS.md`).
- **Constraint**: Do NOT attempt to modify, overwrite, or bypass protections on global `AGENTS.md` files using file-writing tools, permission requests, or raw terminal bypasses (like `cat << 'EOF'`). This is a critical AI Safety rule to prevent agents from altering their own constraints.
- **Protocol**: If a global rule needs to be updated to match a skill, explicitly provide the exact text diff or replacement snippet to the user, and ask them to manually apply the update to their global configuration.

## 2. Halting vs. Skipping in Multi-Element Operations
When processing queues, lists, or batch items (such as bug triage loops, bulk refactoring, or multi-file analysis):
- **Single-Target Requests**: If the user explicitly asks for a specific ID, file, or target, and that target is out of scope, invalid, or closed, the agent MUST immediately notify the user and halt.
- **Batch Requests**: If processing a list (e.g., "triage bugs", "fix all errors"), the agent MUST gracefully and silently **skip** out-of-scope items (e.g., resolved bugs, untracked files) and continue sequential execution of the remaining active targets. Never break or halt a batch loop on an out-of-scope item unless explicitly requested.
