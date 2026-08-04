# Cloudtop Git Velocity & Compound Execution Standards

In Google Cloudtop and corporate development environments, individual Git commands can stall for 15–90 seconds due to corporate hooks, networked filesystem locks, and multi-key SSH FIDO2 identity scans. These rules govern how AI agents execute Git operations to maintain high velocity.

## 1. Mandate Compound Git Execution (No Diagnostic Spam)
- **Constraint**: When performing `/checkpoint`, staging, committing, or pushing changes, **NEVER execute multiple sequential tool calls** for diagnostic Git commands (`git config --get`, `git rev-parse`, `git status`, `git remote -v`, etc.).
- **Protocol**: Bundle staging, committing, and pushing into a **single chained bash command** or script within one tool call:
  ```bash
  git add <files> && git commit -m "<message>" && git push
  ```
- Only run standalone diagnostic commands if an atomic commit or push command explicitly fails and requires debugging.

## 2. Avoid Redundant Identity & Config Checks
- **Constraint**: Do NOT execute `git config --get user.name` or `git config --get user.email` before every commit.
- **Protocol**: Assume the user's Git identity is already properly configured in the Cloudtop environment. Proceed directly to `git commit`.

## 3. Atomic Submodule & Parent Repo Coordination
- **Constraint**: When operating inside a project that is a subdirectory of a parent Git repository or contains submodules, do not ping-pong between directories with separate tool calls.
- **Protocol**: Execute a single compound command that commits the submodule change, stages the submodule SHA in the parent repository, and pushes:
  ```bash
  (cd submodule_dir && git commit -a -m "...") && git add submodule_dir && git commit -m "..." && git push
  ```
