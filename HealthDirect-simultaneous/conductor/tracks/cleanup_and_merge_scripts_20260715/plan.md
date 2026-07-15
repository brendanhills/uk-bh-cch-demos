# Plan: Cleanup and Merge Codebase Scripts (`cleanup_and_merge_scripts`)

## Phase 1: Codebase Audit & Setup
- [ ] **Task 1.1**: Audit and list all root-level `.py` scripts, documenting which are active core tools versus redundant or single-purpose scripts.
- [ ] **Task 1.2**: Check git status and establish sandbox readiness.

## Phase 2: Audio Generator Consolidation & Pruning
- [ ] **Task 2.1**: Merge any unique parameters, prompt adjustments, or voice mappings from `generate_arabic_audio.py` and `generate_spanish_audio.py` into the multi-lingual generators `generate_bilingual_audio.py` and `generate_simultaneous_audio.py`.
- [ ] **Task 2.2**: Delete the obsolete single-language hardcoded script files `generate_arabic_audio.py` and `generate_spanish_audio.py`.
- [ ] **Task 2.3**: Verify that the remaining multi-lingual generators execute correctly to produce correct sample audios.

## Phase 3: Utility Stabilization & Clean Workspace
- [ ] **Task 3.1**: Preserve `list_vertex_models.py` at the root and document its usage. Ensure `glossary_highlighter.py` is properly integrated.
- [ ] **Task 3.2**: Delete temporary and local log/json leftovers (`conversation_transcript.log`, `interpreter_session.log`, `timing_report.json`) and verify that `.gitignore` correctly ignores developer-local runtime logs.

## Phase 4: Regression Testing & Verification
- [ ] **Task 4.1**: Execute the entire automated test suite (`pytest`) to ensure no imports or references were broken by the file reorganization.
- [ ] **Task 4.2**: Verify that the web application `demo/web_server.py` boots and operates smoothly.
