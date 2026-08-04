# Track Specification: Explicit Gemini Context Caching

## Overview
Implement explicit Gemini API Context Caching (`client.caches.create(...)`) in `demo/web_server.py` to persist static system instructions and clinical glossaries (~3,000 tokens) across live translation sessions, eliminating un-cached prompt reprocessing and ensuring high cache-hit efficiency.

## Functional Requirements
1. **Explicit Cache Creation (`client.caches.create`):**
   - On language initialization or live session setup in `web_server.py`, assemble system instructions and clinical glossaries for both directions:
     - `p_to_n` (Patient to Nurse)
     - `n_to_p` (Nurse to Patient)
   - Create two dedicated Gemini Context Cache objects via `client.caches.create(...)` using `google-genai` SDK with a 30-minute (`1800s`) TTL.
2. **Session Configuration Integration (`LiveConnectConfig`):**
   - Reference `cached_content=cache_p_to_n.name` in `config_p_to_n` (`types.LiveConnectConfig`).
   - Reference `cached_content=cache_n_to_p.name` in `config_n_to_p` (`types.LiveConnectConfig`).
3. **Fallback & Error Handling:**
   - Fall back gracefully to inline `system_instruction` text if cache creation fails or is unsupported by the endpoint.
4. **Configuration & Parameters:**
   - Update `demo/interpreter_config.json` to include `"cache_ttl_seconds": 1800` and `"enable_context_caching": true`.

## Non-Functional Requirements
- **Low Latency:** Fast session connection startup without blocking the event loop during cache creation.
- **Cache Hit Efficiency:** Maintain 100% cache-hit ratio for static prompt inputs.

## Acceptance Criteria
- [ ] Server creates separate 30-minute Gemini Context Cache objects for `p_to_n` and `n_to_p` sessions using `client.caches.create`.
- [ ] `LiveConnectConfig` instances link `cached_content` using the created cache resource names.
- [ ] Unit tests pass verifying cache creation, configuration fallback, and session connection parameters.

## Out of Scope
- Modifying client-side audio streaming or microphone VAD capture logic.
