---
description: Process for renaming variables, functions, or files significantly.
---

1.  **Search**:
    -   `grep_search` or `find_by_name` for the *exact symbol* to be renamed.
    -   Note down all occurrences (definitions AND usages).
2.  **Plan**:
    -   Decide if this is a "Replace All" or "Context Sensitive" change.
3.  **Apply Change**:
    -   Update the definition.
    -   Update all usages found in Step 1.
    -   **CRITICAL**: Check imports. If renaming a file/module, update `import` statements in other files.
4.  **Verify**:
    -   Run unit tests that cover the modified component.
    -   Check for `AttributeError` or `ImportError` specifically.
