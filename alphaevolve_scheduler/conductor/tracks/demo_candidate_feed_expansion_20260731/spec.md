# Specification: Update Demo Mode Feed to Recorded Candidates (Progressive Streaming)

## Overview
This track updates the Demo Mode candidate feed from previous static fixtures to recorded candidates (starting with the 8 candidates captured from the latest demo run to confirm and verify the progressive streaming approach, then scaling to 10+). Recorded candidate mutations are scored against hospital priorities using `safe_evaluate()` and persisted into `data/candidates_feed.jsonl` and `fixtures/mock_candidates_feed.jsonl` as permanent fixture data. In Demo Mode, the recorded candidate dataset is streamed to the frontend progressively—revealing 1 candidate every 5–10 seconds—simulating live AlphaEvolve engine execution without custom demo controls.

## Functional Requirements
1. **Recorded Candidate Feed Dataset:**
   - Use the 8 candidates (`Cand_0` to `Cand_7`) captured from the AlphaEvolve run for initial progressive streaming verification, with capability to scale to 10+.
   - Candidate statuses (`BASELINE`, `ACCEPTED`, `REJECTED`, `REPLANNED`) are preserved directly from AlphaEvolve output.
   - Every candidate entry includes score, scheduled patients, overtime hours, idle time, fatigue violations, candidate title, summary insight, and candidate code.

2. **Persistence & Permanent Fixture Integration:**
   - Store candidate entries in `data/candidates_feed.jsonl`.
   - Commit `fixtures/mock_candidates_feed.jsonl` with recorded candidates as a permanent fixture set of the demo suite.

3. **Progressive Frontend UI Feed Rendering:**
   - In Demo Mode, load `mock_candidates_feed.jsonl` and stream candidates progressively (1 candidate revealed every 5–10 seconds) to simulate live AlphaEvolve execution.
   - Update candidate step indicators and polling badges to accurately reflect candidate progression.
   - Ensure Phase 3 candidate selection dropdown populates all non-rejected candidates from the expanded feed.

## Non-Functional Requirements
- **Progressive Streaming Pace:** Display 1 candidate every 5–10 seconds in Demo Mode to simulate real AlphaEvolve iterations.

## Acceptance Criteria
- `fixtures/mock_candidates_feed.jsonl` contains the 8 recorded candidate records from the demo run (Cand_0 through Cand_7).
- Demo Mode progressively streams and renders 1 candidate every 5–10 seconds into the Candidate Feed table.
- Phase 3 candidate selection dropdown displays all valid evolved candidates from the recorded set.
- All candidates in the feed are verified by `safe_evaluate` to guarantee valid scheduling metrics.
