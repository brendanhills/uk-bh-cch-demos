---
description: Process for verifying generated content meets system constraints.
---

1.  **Define Constraints**: Before generating, know the limits (e.g., Token Limit = 1M, File Size = 10MB).
2.  **Generate Content**: Run the generation script.
3.  **Verify Size**:
    -   Check file size: `ls -lh path/to/file`.
    -   Estimate Token Count: `(File Size in Bytes) / 4` (rough heuristic).
4.  **Scale Check**:
    -   If content is > 50% of limit, flag as "High Risk".
    -   If "High Risk", implement **Chunking** or **Pagination** immediately. DO NOT assume the model handles it.
5.  **Test Ingestion**:
    -   Run a test script that just *loads* the content (e.g., `consult_policy_docs`) to confirm it doesn't crash or hit API limits.
6.  **Integrate**: Only after Step 5 passes, connect it to the main agent.
