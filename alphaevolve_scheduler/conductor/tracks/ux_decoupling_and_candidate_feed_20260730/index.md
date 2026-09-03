# Specification: Contract-First UX/Logic Decoupling & Candidate Exploration Feed

## 1. Overview
Decouples the RCH web dashboard UX from the Python optimization backend using formal JSON Schema contracts (`data/config.schema.json` and `data/trace.schema.json`). Introduces static mock fixture mode (`🧪 Fixture Mode`) for frontend validation without running the backend, and adds a multi-destination **Candidate Exploration Feed** (UI tab, JSONL log, and STDOUT terminal logs) to explain real-time AlphaEvolve algorithm mutations.

## 2. Key Objectives
- Define formal JSON Schemas (`data/config.schema.json` and `data/trace.schema.json`) for hospital resources, specialist clinical teams (`requiredTeam`), disruptions, and candidate step traces.
- Provide a static fixture suite (`fixtures/`) and live manual validation script (`scripts/simulate_live_backend_update.py`) demonstrating frontend UI updates without frontend code changes.
- Add an interactive **Candidate Feed** tab in `rch/index.html` displaying step/generation, score, metrics, and plain-English "Why Better / Worse" AlphaEvolve insights.
- Enhance UI dashboard clarity with an executive **Detailed Operational Scenario & Clinical Co-Scheduling Scope Panel** inside the **Scenario Breakdown** tab.

## 3. Success Criteria
- 100% automated test suite passing (`experiment/test_contract_schemas.py` and `experiment/test_rch_html.py`).
- Clean separation of UI rendering from backend python execution.
