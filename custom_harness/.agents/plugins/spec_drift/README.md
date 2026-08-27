# Spec Drift Plugin (`spec_drift`)

A specification drift detection and architecture alignment skill for Antigravity, Jetski, and developer environments.

## 📦 Included Skill

| Skill | Slash Command | Description |
| :--- | :--- | :--- |
| **spec_drift** | `/spec_drift` or `/drift` | Two-pass specification drift detector. Filters candidate specs via YAML frontmatter (`*spec.md`) or mapping configs, evaluates contract drift, assigns severity (`CRITICAL`, `WARNING`, `INFORMATIONAL`), provides triage recommendations (`Adopt Code` vs `Fix Code`), and generates ready-to-apply spec patch diffs. |

## 🛠️ Architecture
- **Pass 1 (Filtering & Discovery)**: `drift_detector.py` scans candidate specifications from modified files using YAML frontmatter or mapping definitions.
- **Pass 2 (Divergence & Triage)**: Analyzes diffs against specifications, checking data contracts, API routes, and invariants, outputting severity ratings and suggested spec patches.
- **Hermetic Testing**: Automated unit tests using standard library `unittest`.
