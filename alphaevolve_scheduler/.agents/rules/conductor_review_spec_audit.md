# Conductor Codebase vs. Spec Audit Rule

When executing `/conductor-review`, `/conductor-status`, or reviewing any Conductor track:
1. **Specification vs. Codebase Audit Protocol (CRITICAL):**
   - **Code-Level Verification:** Do NOT trust `[x]` checkmarks in `plan.md`. For every bullet point in the track's `spec.md` (and `product-guidelines.md`), verify that the functional requirement is actually implemented in the codebase (e.g., check for required DOM element IDs, UI button labels, CSS animations, and backend constraint evaluations).
   - **Incomplete Track Flagging:** If any functional requirement in `spec.md` is missing from the codebase or has an open bug reported against it:
     - Mark the track as **`[~]` In Progress** in `conductor/tracks.md`.
     - Reopen the corresponding tasks as unchecked (`[ ]`) in `plan.md` or append a dedicated fix phase.
     - Record the missing requirement in `.agents/bugs.json` with status `"Reported"`.
