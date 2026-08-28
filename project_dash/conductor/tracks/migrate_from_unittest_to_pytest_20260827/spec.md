# Specification: Migrate Test Suite from Unittest to Idiomatic Pytest

## Overview
Migrate the Project Dash test suite from legacy Python `unittest.TestCase` classes to modern, idiomatic `pytest` conventions. Establish centralized fixtures (`conftest.py`), configure root `pyproject.toml` test discovery, convert assertions to native Python `assert` expressions with rich diff reporting, and leverage `@pytest.mark.parametrize` and `tmp_path` fixtures for cleaner, faster, and more maintainable automated testing.

## Core Problem Statement
1. **Module Resolution Friction**: Running `pytest` directly from the project root fails unless invoked with `python3 -m pytest` or `PYTHONPATH=.` because `pyproject.toml` lacks explicit `[tool.pytest.ini_options]` configuration.
2. **Boilerplate & Verbose Class Structures**: 21 test files rely on class-based `unittest.TestCase` structures, verbose assertions (`self.assertEqual`, `self.assertTrue`, `self.assertIn`, `self.assertDictEqual`, `self.assertIsNone`), and custom setup routines instead of lightweight test functions and dependency-injected fixtures.
3. **Repeated Fixture & Mock Logic**: Repeated setup for sample datasets (Aurora showcase, Monaro configs, mock risk/issue registers, temporary directories) is copy-pasted across multiple test files rather than shared cleanly in `conftest.py`.
4. **Suboptimal Parametrization**: Several test suites use manual for-loops to test multiple cases, making failure diagnosis harder compared to `@pytest.mark.parametrize`.

## Functional Requirements

1. **Pytest Root Configuration (`pyproject.toml`)**:
   - Configure `[tool.pytest.ini_options]` with:
     ```toml
     [tool.pytest.ini_options]
     pythonpath = ["."]
     testpaths = ["tests"]
     python_files = ["test_*.py"]
     python_functions = ["test_*"]
     filterwarnings = ["ignore::DeprecationWarning"]
     addopts = "-v --tb=short"
     ```
   - Ensure running `pytest` directly from the project directory works reliably without requiring `-m` or manual `PYTHONPATH` exports.

2. **Centralized Test Fixtures (`tests/conftest.py`)**:
   - Provide standard reusable fixtures:
     - `sample_project_dir`: Returns path to `data/sample/`.
     - `sample_config`, `sample_risks`, `sample_issues`, `sample_snapshots`: Pre-loaded JSON fixtures.
     - `mock_pipeline_env`: Sets up mock environment variables and temporary data directories using pytest's `tmp_path`.
     - `mock_server_client`: Helper fixture for making HTTP requests to a test server or handler instance.

3. **Idiomatic Test Suite Refactoring**:
   - Refactor all 21 test files in `tests/`:
     - Convert `unittest.TestCase` classes to modular top-level functions (`test_*`).
     - Replace `self.assertEqual(a, b)` and related calls with native Python `assert a == b`.
     - Replace `self.assertRaises(Exception)` with `pytest.raises(Exception)`.
     - Replace iterative loops with `@pytest.mark.parametrize`.
     - Replace manual directory creation/deletion with pytest's built-in `tmp_path` and `monkeypatch`.

4. **100% Invariant & Coverage Preservation**:
   - Preserve all existing 127 test coverage cases across pure analytics, data integrity, Gemini generation, pipeline ingestion, server REST handlers, and presentation decoupling.
   - Maintain 100% pass rate with improved execution speed (< 2.5s).

5. **Tooling & Documentation Alignment**:
   - Update `conductor/tech-stack.md`, `README.md`, `Resume.md`, and `docs/HANDOVER_GUIDE.md` to reference `pytest` commands.

## Acceptance Criteria
- [ ] Direct invocation of `pytest` from `project_dash/` passes without requiring `python3 -m pytest` or `PYTHONPATH=.`.
- [ ] `tests/conftest.py` is established with shared fixtures.
- [ ] All test files in `tests/` use idiomatic pytest functions and native `assert` statements.
- [ ] All 127+ test cases pass 100% with zero regressions.
- [ ] Documentation updated across `README.md`, `Resume.md`, and Conductor specifications.
