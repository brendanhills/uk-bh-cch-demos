# Custom Harness — Compaction Summary & Resume State

**Last Updated**: 2026-07-29  
**Current Branch**: `feature/prompt-heuristics`

---

## 🎯 Architecture & State Summary

### 1. Standalone Customization Engine (Symlinked)
- The global standalone discovery engine (`~/.gemini/config/`) ignores declarative JSON manifests (`skills.json`, `rules.json`, `plugins.json`).
- All global skills and rules are dynamically symlinked from this repository using the Universal Customization Installer (`python3 ~/.gemini/config/templates/install_customizations/register_customizations.py`).

### 2. Consolidated Bug Management Protocol (`.agents/skills`)
- Duplicate Conductor bug skills (`conductor-bug*`) have been permanently removed.
- **`/bug`**: Rapid bug logging with empty priority/impact fields.
- **`/triage_bug [#id]`**: Investigates root cause, assigns priority/impact, and outlines a plan. Silently skips resolved/closed bugs in batch mode.
- **`/list_bugs`**: Renders a premium Markdown table with scope filtering (`all`/`resolved`) and Priority-tier grouping (`P0` first).
- **`/fix_bug [#id]`**: Adopts **Adaptive Tiered Verification** (Tier 1 fast-path, Tier 2 suite augmentation, Tier 3 reproduction test) with a **2-Retry Circuit Breaker** against test-debugging loops.

### 3. Active Global Rules (`.agents/rules`)
- **`cloudtop_git_velocity.md`**: Enforces atomic, compound Git execution (`git add ... && git commit ... && git push`) and forbids sequential diagnostic spam to prevent corporate SSH/FIDO2 latency stalls.
- **`pragmatic_testing_standards.md`**: Enforces Implementation-First Velocity (no default TDD in normal chat), the 3-Tier Test Execution Heuristics Matrix (including explicit skipping of backend tests for Frontend UI/CSS visual styling), and the 2-Retry Test-Debugging Circuit Breaker.
- **`standalone_customization_architecture.md`**: Mandates symlink architecture for global extensions in Standalone Jetski and Antigravity.
- **`agent_safety_and_batch_standards.md`**: Prohibits agents from modifying system-protected global `AGENTS.md` files and defines Skipping vs. Halting standards for batch operations.

---

## 🚀 Next Steps / Ready State
- The workspace is clean and fully synchronized with `~/.gemini/config/`.
- Ready for new feature tracks, prompt optimization runs, or daily engineering tasks.
