# Specification - Cleanup Legacy Kmart Files

## Overview
This track removes legacy Kmart retail supply-chain demo files (`make_network.py`, `network.json`, `traces/` directory, `reconstruct_candidate_routes.py`, `setup_engine.sh`, `simulate_trace.py`) from active project directories (`data/`, `scripts/`, `traces/`). These files are redundant copies of files already preserved in `legacy_kmart/`. Cleaning them up untangles active project paths for the Cymbal Children's Hospital (CCH) co-scheduling demo while preserving full backward compatibility for the legacy Kmart demo under `legacy_kmart/`.

## Functional Requirements
- **FR1**: Remove redundant Kmart-specific files from `data/`:
  - `data/make_network.py`
  - `data/network.json`
- **FR2**: Remove redundant Kmart-specific files from `scripts/`:
  - `scripts/reconstruct_candidate_routes.py`
  - `scripts/setup_engine.sh`
  - `scripts/simulate_trace.py`
- **FR3**: Remove redundant Kmart-specific `traces/` directory from the root workspace (`traces/candidates.jsonl`, `traces/evolution_trace.json`, `traces/evolution_trace.orig.json`, `traces/run.log`).
- **FR4**: Preserve all identical files inside `legacy_kmart/` (`legacy_kmart/data/`, `legacy_kmart/scripts/`, `legacy_kmart/traces/`).
- **FR5**: Ensure no CCH demo files, data fixtures (`data/config.json`, `data/candidates_feed.jsonl`, `data/traces_*.jsonl`), or experiment code (`experiment/`) are modified or deleted.

## Non-Functional Requirements
- **NFR1**: All 45 unit & integration tests in `experiment/` must continue to pass without error.
- **NFR2**: Zero broken references in `server.py` or CCH dashboard (`cch/index.html`).

## Acceptance Criteria
- [ ] `data/make_network.py` and `data/network.json` are removed from Git tracking and filesystem in `data/`.
- [ ] `scripts/reconstruct_candidate_routes.py`, `scripts/setup_engine.sh`, and `scripts/simulate_trace.py` are removed from Git tracking and filesystem in `scripts/`.
- [ ] `traces/` directory is removed from Git tracking and filesystem in root.
- [ ] `legacy_kmart/` directory contents remain completely intact and functional.
- [ ] Test suite (`PYTHONPATH=. uv run python -m unittest discover -s experiment -p "test_*.py"`) passes 100% of tests.

## Out of Scope
- Modifying `legacy_kmart/` contents.
- Modifying CCH frontend (`cch/index.html`) or CCH backend (`experiment/`).
