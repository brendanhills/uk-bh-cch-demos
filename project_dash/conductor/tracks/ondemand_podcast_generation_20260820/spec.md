# Specification: On-Demand Backend Podcast Generation

## Overview
Enable on-demand backend podcast generation for any reporting cycle. When audio is missing for a week, clicking Play or Generate triggers a backend API endpoint (`POST /api/generate-podcast`) that uses Gemini 3.5 to generate the multi-speaker transcript and renders the authentic high-fidelity audio asset.

## Functional Requirements
1. **Backend Endpoint (`POST /api/generate-podcast`)**:
   - Accept parameters: `{ project: string, week: string, force_regenerate?: boolean }`.
   - Read weekly snapshot context from `data/<project>/snapshots.json` and domain risk/issue metrics.
   - Use Gemini 3.5 (`scripts.gemini_generator.generate_multispeaker_podcast`) to produce conversational dual-host dialogue (Alex & Jordan).
   - Render multi-speaker audio and persist to `assets/podcast_<project>_<week>.mp3` or dynamic asset storage.
   - Update `snapshots.json` with the new audio URL, duration, and dialogue script.
   - Return `{ status: "ok", audioUrl: string, duration: string, script: Array }`.

2. **Frontend Player & Loading UX**:
   - Detect if audio exists for the active week.
   - If missing, replace playback with an interactive loading state (`⏳ Generating high-fidelity podcast briefing for Week X...`) and disable playback buttons during generation.
   - Automatically bind the rendered audio source upon completion, refresh the transcript modal, and initiate playback seamlessly.
   - Add explicit "Regenerate Podcast" action in the transcript modal.

3. **Error Handling & Resiliency**:
   - Surface actionable error toasts if generation fails or API credentials are misconfigured.
   - Eliminate synthetic client-side speech synthesis fallbacks in favor of deterministic backend audio generation.

## Acceptance Criteria
- [ ] `POST /api/generate-podcast` generates valid podcast transcript and audio metadata for any reporting week.
- [ ] Frontend triggers backend generation with loading spinner when audio is not yet generated.
- [ ] Rendered audio automatically plays and updates transcript modal upon completion.
- [ ] Unit and integration regression tests verify API contract and frontend state management.
