# Resume Tasks

## Next Steps

- [ ] **Investigator Agent Refactoring completion**:
    - [ ] `loan_approval_agent/sub_agents/investigator/tools.py` was converted to async, but we need to ensure `test_agents.py` fully covers it (it passed, but verify coverage).
    - [ ] Verify `check_data_consistency` and `calculate_dti` are working correctly in async mode with `test_async_migration.py` if needed (currently they were not explicitly added there but `test_agents.py` covers them).
    - [ ] **Migrate Doc Analyzer**: Move `loan_agent/tools/doc_analyzer.py` to `loan_approval_agent/tools/` and update `test_document_upload.py` to use the new agent.

- [ ] **Integration Testing**:
    - [ ] Run `tests/integration/test_manual_scenarios.py` to ensure the full flow works with the new async tools.
    - [ ] Verify `tests/test_model_features.py` (if it exists or needs creation per implementation plan).

- [ ] **Deployment Preparation**:
    - [ ] Check `docs/DEPLOYMENT_PLAN.md` and prepare for Cloud Run deployment if prioritized.

- [ ] **Cleanup**:
    - [ ] Remove `risk_analyst` references from any remaining non-code files (we did a good sweep, but double check config/env if any).
