---
name: bug_plan
description: Create a phased implementation plan for addressing the current bug list, balancing priority vs implementation risk (with support for demo/launch modes).
---

# Phased Bug Implementation Plan Command (`/bug_plan`)

When the user runs `/bug_plan` (or `/bug_plan demo`, `/bug_plan launch`):

1. **Automatic Triage Guard**:
   - Inspect `<workspace-root>/.agents/bugs.json`.
   - If any active bugs have unassigned `priority`, `impact`, or `risk` (empty `""`), automatically execute triage on them first (investigating root cause, assigning `priority` `P0`-`P3`, `impact` `Critical`-`Low`, `risk` `Low`-`High`, setting `"date_triaged"` to current date, and updating status to `"Investigated"`). Save these updates to `.agents/bugs.json`.

2. **Mode & Strategy Selection**:
   - **Default (`/bug_plan`)**: Balanced strategy. Phase 1 targets critical/high-impact bugs with low/medium risk, Phase 2 targets higher-risk critical fixes, Phase 3/4 target lower impact polish.
   - **Demo / Launch Mode (`/bug_plan demo`, `/bug_plan launch`)**: Low-risk stability strategy. Prioritizes quick wins, low-risk UI/UX fixes, and stability polish into Phase 1 to minimize regression risk ahead of upcoming demos or releases.

3. **Phase Assignment**:
   - Filter out resolved, fixed, closed, or obsolete bugs (`"Fix Verified"`, `"Closed"`, `"Obsolete"`).
   - Assign remaining active bugs to phases:
     - **Phase 1**: Immediate Priority / Low-Risk Focus.
     - **Phase 2**: Core Functional Fixes.
     - **Phase 3**: Non-blocking Polish & Secondary Improvements.
     - **Phase 4**: Low Priority / Backlog items.
   - Update `<workspace-root>/.agents/bugs.json` with assigned `"risk"` (`"Low"`, `"Medium"`, `"High"`) and `"phase"` (`"Phase 1"`, `"Phase 2"`, etc.) for each bug.

4. **MANDATORY ARTIFACT CREATION**:
   - **YOU MUST WRITE** the full plan document to `<workspace-root>/.agents/bug_plan.md` containing:
     - **Executive Summary**: Overview of strategy and target mode (e.g. Balanced vs Demo/Launch).
     - **Phased Roadmap**: Structured breakdown of each phase (bugs included, root cause summary, proposed fix strategy, verification method, risk profile).
     - **Execution Sequence & Dependencies**: Estimated sequence and inter-bug dependencies.

5. **Output Summary**:
   - Present a concise, structured markdown table in the conversation summarizing the phased execution roadmap and link to `.agents/bug_plan.md`.
