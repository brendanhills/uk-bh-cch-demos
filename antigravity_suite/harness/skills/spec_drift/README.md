<!--* freshness: { owner: "dleeeee" reviewed: "2026-06-18" } *-->

# Spec Drift Detector

This skill detects if code changes in a changelist (CL) cause corresponding
Markdown specifications to go out of sync (drift). It helps ensure documentation
remains updated by using a two-pass approach: first filtering with static
mappings to identify affected specs, and then using an LLM to check for actual
behavioral drift against the diff.

## Quirks

Important: See http://b/525426502 for more details about the following bug.

Code Review Agent does not support the `configPath` field in `agent.json`. We
have to manually copy the `config.yaml` into a `config` field in `agent.json` in
order for Code Review Agent to correctly load the custom agent prompts.

## How to Test

### Unit Test

You can test this skill using `evalin`. Run the following exact command:

```bash
/google/bin/releases/gemini-agents-evalin/evalin.par run net/slo/l3/_agents/skills/spec_drift_detector/EVAL.txtpb --agents="net/slo/l3/_agents/skills/spec_drift_detector/agents.json"  --model=MODEL_PLACEHOLDER_M18
```

#### Notes on the Command:

*   For more information on testing with this tool, see the
    [evalin documentation](http://go/evalin).
*   **Model Choice:** The model flag (`--model=MODEL_PLACEHOLDER_M18`) is chosen
    specifically to match the same model used by `go/cl-review-agent`.

### Code Review Agent Test

To test this skill on an actual cl, ensure the skill is setup as part of
AGENTIC_REVIEW and run the following exact command:

```bash
blaze run //learning/gemini/_agents/cl_review_agent:cl_review_agent -- review --cl={CLNUMBER} --dry_run=true --get_skills_from_metadata --agent_name="Skills Review Agent" --model=MODEL_PLACEHOLDER_M18
```

#### Notes on the Command:

*   For more information on testing Code Review Agent, see the
    [documentation](http://go/cl-review-agent).
*   **Model Choice:** The model flag (`--model=MODEL_PLACEHOLDER_M18`) is chosen
    specifically to match the same model used by `go/cl-review-agent`.
