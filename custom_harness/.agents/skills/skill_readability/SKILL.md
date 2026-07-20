---
name: skill-readability
description: >-
  Reviews CLs against the guidelines and criteria established by the
  skill-creator skill. Use when you need to review a CL that creates, updates,
  or tests an Agent Skill. Agent skills are found in directories with a
  `SKILL.md` file. Do not use for non-skill code.
---

# Skill Readability Review

This skill guides the review of CLs targeting Agent Skills. It ensures skills
are well-structured, have good test coverage, and follow the standard
skill-creator patterns.

## Apply Review Criteria

1.  Read and apply the review criteria from the `skill-creator` reference docs.
    Use code_search with `file:` filter to find and read each:
    -   Content quality & structure:
        `file:learning/gemini/agents/skills/skill_creator/references/reviewing.md`
    -   Eval/test quality (applies to both EVAL.txtpb and TEST.md):
        `file:learning/gemini/agents/skills/eval_creator/SKILL.md`
    -   Skill creation:
        `file:learning/gemini/agents/skills/skill_creator/SKILL.md`
2.  Evaluate the CL diff against the guidelines and structure rules in those
    references.
3.  **MANDATORY:** Check for duplicate or overlapping skills using the
    `skill-finder` skill.
    -   Query it for keywords related to the new skill to see if there is an
        existing known skill across the codebase that shares significant overlap
        or intent.
    -   **Crucial:** To avoid terminal output truncation when searching, output
        the results to a file and read the file using `view_file`.
    -   If an existing skill could just be extended instead (like finding
        `coverage` when asked to review `blaze-coverage`), note this in your
        review. You must halt the review and flag the duplicate strongly.
    -   **Important:** Use the full path returned by `skill-finder` when
        referencing the skill. Do not assume it is in
        `learning/gemini/agents/skills/`.
4.  If there are changes to source files in the CL, you MUST search for an
    appropriate language readability skill. Use code search with a query like
    `f:SKILL.md` scoped to `google3/learning/gemini/agents/skills/` to find it,
    and apply its criteria to the review on these files.
5.  **Verify SKILL.md synchronization (for skills using CLIs):** If a skill
    relies on a CLI tool and the CL updates agent-facing features or subcommands
    in `learning/gemini/agents/clis/`, verify that the corresponding `SKILL.md`
    is updated to document how the agent should use the new capabilities.

## Verify Eval Report Tag

For CLs touching skill or CLI directories, verify the CL description includes an
`EVALIN_REPORT=<url>` tag linking to an evalin ablation report. Running evalin
is the expected path for almost all skill CLs.

**SKILL.md and references/ files are NOT documentation** — they are the skill's
executable instructions that directly control agent behavior. Changing them IS a
behavioral change and MUST be evaluated.

Only in exceptional cases (e.g. OWNERS file changes, BUILD-only refactors with
no instruction changes) should the description contain `SKIP_EVAL=<reason>` —
this is strongly discouraged. Flag missing tags as a review comment — the
METADATA presubmit will also warn, but catching it during review is faster
feedback.

See `go/testing-skills` for instructions on running evals and generating
reports.

## Run Tests

After reviewing the code, run the skill's tests to verify it works. Skills may
have an `EVAL.txtpb`, a `TEST.md`, or both. You MUST test against the actual CL
changes, not the base workspace.

### Set up a temporary workspace with the CL

Create a temporary CitC workspace with the CL patched in:

```bash
g4 citc review_tmp_<cl_number>
cd /google/src/cloud/<your_username>/review_tmp_<cl_number>/google3
g4 patch -c <cl_number> -t default
```

Use this workspace for ALL build/test commands below.

### Run the tests

1.  From the CL diff, identify which skill directory(ies) are modified.
2.  For each modified skill, check for both `TEST.md` and `EVAL.txtpb`.
3.  Read the `eval-creator` skill's **running_tests.md** reference for detailed
    execution instructions for both formats (search for
    `file:learning/gemini/agents/skills/eval_creator/references/running_tests.md`).
4.  If the skill has neither TEST.md nor EVAL.txtpb, note it as untestable and
    recommend adding an EVAL.txtpb.

### Clean up

After all tests are done, delete the temporary workspace:

```bash
g4 citc -d -f review_tmp_<cl_number>
```

### Report results

Include a test results summary in your review comment. **Formatting**: Always
put a blank line before markdown tables, otherwise they won't render correctly.

Example:

```markdown
**Test Results** (tested with CL changes patched in):

Test               | Result | Notes
------------------ | ------ | -----------------------
Build              | ✅      |
Unit test          | ✅      |
Functional: search | ✅      | Returns expected output
Evalin ablation    | ✅      | +15% with skill vs without
```

## Reporting Issues

Report bugs or improvements for this skill at
[Agent Skill: skill_readability](http://b/hotlists/8077995). See the
`skill_issue` skill for instructions on filing and triaging skill bugs.
