# Implementation Plan - HealthDirect Medical Glossary & Term Translation Support

## Phase 1: Glossary Data & Lookup Module (`app/glossary.py`)
- [ ] Task: Port `glossary.json` subset and create `app/glossary.py` term lookup module supporting formal/informal queries across English, Arabic, and Hindi
- [ ] Task: Create `tests/test_glossary.py` with unit tests for formal/informal term lookups
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: System Instruction & Prompt Integration
- [ ] Task: Update `CCH_SYSTEM_INSTRUCTION` in `app/cch_agent/agent.py` with natural medical explanation rules (explain formal clinical terms using informal layman equivalents)
- [ ] Task: Add test in `tests/test_agent_instruction.py` verifying medical term explanation prompt rules
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Glossary Highlighting & End-to-End Verification
- [ ] Task: Adapt `app/glossary_highlighter.py` to highlight recognized medical terms in transcript logging and event console
- [ ] Task: Run full test suite (`pytest`) and verify clean pass
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
