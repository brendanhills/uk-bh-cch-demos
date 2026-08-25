---
name: spec-drift-detector
description: >-
  Detects if code changes in a CL cause corresponding markdown specifications
  (specs) to go out of sync (drift). Use during CL review to ensure documentation
  remains updated.
---

# Spec Drift Detector

This skill detects when code changes drift from their specifications. It uses a
two-pass approach:

1.  **Pass 1 (Filtering)**: Identifies which specifications might be affected by
    the changed files using hybrid discovery: static mapping configurations
    (`spec_mappings.json`) and/or markdown specification YAML frontmatter
    declarations (`*spec.md`).
2.  **Pass 2 (Divergence Checking)**: Uses an LLM to compare the diff of the
    matched files against the specification content to determine if there is a
    true behavioral drift (excluding innocuous changes like refactoring,
    formatting, logging, or bug fixes that align with the spec), classify
    severity, and generate suggested spec patches.

## Instructions

### Step 1: Get File Changes & Diffs

1.  **Identify the Target Files**:

    -   First, check if the user prompt explicitly specifies which files to
        review (e.g. `Review the changes in net/slo/l3/dummy_code.cc`). If so,
        use that file path.
    -   If the prompt does NOT specify any files, you may run the minimum
        required version control system status command to identify the modified
        files.
    -   If no modified files are found, simply output that no modified files
        were found and end your turn.

2.  **Get Diff**: Follow instructions from the prompt for how to get the diff.

### Step 2: Invoke Subagent

Invoke the `spec_drift_detector` subagent to perform both relevance filtering
and divergence checking.

-   **NO REDUNDANT DEFINITIONS OR TOOL CALLS**: The subagent
    `spec_drift_detector` is already defined by the system. You MUST NOT call
    `define_subagent`, and you MUST NOT run `list_dir` or `view_file` on any
    configuration files inside the skill directory to inspect its definition.
    Simply invoke it directly.
-   **Invoke Tool Call**: Call `invoke_subagent` with the following parameters:

    -   `TypeName`: `spec_drift_detector`
    -   `Workspace`: `inherit`
    -   `Prompt`: Use the following template, replacing the placeholders with
        the actual values:

        ```markdown
        Please check for spec drift.

        [MODIFIED FILES]
        <modified_files>

        [DIFF COMMAND]
        <command to generate diffs>

        [SPEC MAPPINGS CONFIG]
        <absolute_path_to_spec_mappings.json>
        ```

        *Note: The default spec mapping file is usually located at
        `net/slo/l3/_agents/skills/spec_drift_detector/spec_mappings.json`. If no
        mappings file exists, the subagent auto-scans for local frontmatter
        specs.*

-   **Keep-Alive**: Immediately after invoking the subagent, you MUST call the
    `schedule` tool to schedule a one-shot wake-up timer with `DurationSeconds`
    set to `120` and `Prompt` set to `"Check subagent status"`.

### Step 3: Process Findings

The subagent will process the changes, run the relevance filtering script,
compare any matched specs to the diffs, and return a JSON message containing a
list of results.

-   Parse the subagent's response. E.g.:

    ```json
    [
      {
        "spec": "net/slo/g3doc/infrastructure/l3/slo_applies_spec.md",
        "matched_files": ["net/slo/l3/collector/scheduling/prober_flow_filter_evaluator.cc"],
        "verdict": "DRIFT",
        "severity": "CRITICAL",
        "section": "## 2. Threshold Limits",
        "reason": "Default prober threshold was changed from 10 to -5.",
        "suggested_spec_patch": "```diff\n- Default threshold is 10.\n+ Default threshold is -5.\n```"
      }
    ]
    ```

-   For each item where the `verdict` is `DRIFT`:

    -   Leave a comment on the CL (preferably on one of the matched files, or as
        a general CL comment if file-level is not possible).
    -   The comment should follow this template:
        > **Spec Drift Warning (`{severity}`)**: The changes to `{matched_files}` may cause the specification [`{spec_basename}`]({spec_path}) to become out of sync.
        >
        > **Section**: `{section}`
        > **Reason**: `{reason_from_subagent}`
        >
        > **Suggested Spec Patch**:
        > {suggested_spec_patch}
        >
        > Please update the specification or verify that it is still accurate.

-   If the verdict is `NO_DRIFT` or `ERROR` for all specs, or if the list is
    empty (or the subagent reports no drift found), output a final response
    summarizing the findings (or error) and end your turn. Do NOT post a comment
    on the CL for these cases.

