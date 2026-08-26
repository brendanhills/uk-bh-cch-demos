# Spec Drift Plugin (`spec_drift`)

A specification drift detection and architecture alignment plugin suite for Antigravity, Jetski, and Gemini CLI.

## 📦 Included Skills

| Skill | Slash Command | Description |
| :--- | :--- | :--- |
| **spec_drift** | `/spec_drift` or `/drift` | Audits codebase against Conductor `spec.md` or SDDs across 4 layers (data contracts, APIs, UI, AI pipelines) to produce a Discrepancy Review Matrix. |
| **spec_drift_detector** | — | Automated CL review skill that uses hybrid frontmatter & static mappings (`spec_mappings.json`) to detect divergence, classify severity, and generate suggested spec patches. |

## 🛠️ Architecture
- **Filtering (Pass 1)**: `drift_detector.py` identifies candidate specifications from modified files using YAML frontmatter or mapping definitions.
- **Divergence Checking (Pass 2)**: Analyzes diffs against specifications, categorizing into `NO_DRIFT` or `DRIFT` with severity rating (`CRITICAL`, `WARNING`, `INFORMATIONAL`).
- **Universal Testing**: 23 automated unit tests with standard library `unittest` and `absltest` compatibility.
