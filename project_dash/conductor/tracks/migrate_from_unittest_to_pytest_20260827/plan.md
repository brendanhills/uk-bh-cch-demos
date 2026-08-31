# Implementation Plan: Migrate Test Suite from Unittest to Idiomatic Pytest

## Phase 1: Pytest Root Configuration & Shared Fixtures
- [x] Task: Update `pyproject.toml` with `[tool.pytest.ini_options]`
  - [x] Add `pythonpath = ["."]`
  - [x] Add `testpaths = ["tests"]`
  - [x] Add standard flags and warning filters
  - [x] Verify `pytest` runs directly from command line without `python3 -m`
- [x] Task: Create `tests/conftest.py` with shared fixtures
  - [x] Add `sample_dir`, `sample_config`, `sample_risks`, `sample_issues`, `sample_snapshots` fixtures
  - [x] Add `tmp_project_workspace` fixture for isolated test execution
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Core Domain & Ingestion Test Migration
- [ ] Task: Migrate Analytics & Data Integrity Test Suites
  - [ ] Migrate `tests/test_analytics.py` (convert to test functions, use native `assert`)
  - [ ] Migrate `tests/test_data_integrity.py`
  - [ ] Migrate `tests/test_sample_dataset.py`
  - [ ] Migrate `tests/test_modules_integrity.py`
- [ ] Task: Migrate Gemini & Pipeline Ingestion Test Suites
  - [ ] Migrate `tests/test_gemini_generator.py` (use `monkeypatch` and `pytest.raises`)
  - [ ] Migrate `tests/test_pipeline.py` (use `tmp_path` and shared sample fixtures)
  - [ ] Migrate `tests/test_ingest_data.py`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Server, REST API & Presentation Test Migration
- [ ] Task: Migrate Server & API Test Suites
  - [ ] Migrate `tests/test_server.py`
  - [ ] Migrate `tests/test_server_parameterized.py` (leverage `@pytest.mark.parametrize`)
  - [ ] Migrate `tests/test_server_rationalized.py`
- [ ] Task: Migrate UI, Presentation & Phase Bug Suites
  - [ ] Migrate `tests/test_presentation_decoupling.py`
  - [ ] Migrate `tests/test_register_separation.py`
  - [ ] Migrate `tests/test_strategic_advisory.py`
  - [ ] Migrate `tests/test_driver_tree_clickable_risks.py`
  - [ ] Migrate phase bug tests (`tests/test_phase1_bugs.py` through `tests/test_phase6_bugs.py`, `tests/test_phase1_stability.py`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Full Suite Verification & Documentation Alignment
- [ ] Task: Execute full test suite via `pytest` and verify 100% pass rate (127+ tests)
- [ ] Task: Update `README.md`, `Resume.md`, and `conductor/tech-stack.md` testing instructions
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
