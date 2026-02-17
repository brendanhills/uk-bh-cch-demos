---
description: Process for safely changing data schemas (JSON keys, API responses, etc).
---

1.  **Identify the Change**: Define the old key/structure and the new key/structure.
2.  **Search Usage**:
    -   Run `grep_search` for the *OLD* key across the entire codebase.
    -   Identify all files that consume this data (Agents, UI, Scripts).
3.  **Update Producers**:
    -   Modify the mock data generators or static JSON files (`data/`).
4.  **Update Consumers**:
    -   Update all identified files from Step 2 to use the *NEW* key.
5.  **Verify**:
    -   Run unit tests.
    -   If it's a UI driven value, manually verify the UI component specifically.
6.  **Cleanup**:
    -   Run `grep_search` again for the *OLD* key to ensure 0 results (unless strictly required for backward compatibility).
