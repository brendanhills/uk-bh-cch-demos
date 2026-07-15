# Specification: Passive Interpreter Resiliency & End-to-End Testing (`resiliency_testing_20260715`)

This track implements robust backend exception catching for real-time WebSocket connection drops, immediate error bubbling to paired frontend clients, and scaffolds testing dependencies for future browser-based E2E verification.

## 1. Overview
During active simultaneous transcription and translation calls, external network drops or Gemini API Gateway timeouts can abruptly close active streaming sockets. To prevent server hangs or silent failures, the backend must actively catch connection exceptions, bubble the error state to both clinicians and patients, shut down streaming threads cleanly, and assert this resilience programmatically using headless chaos integration tests.

---

## 2. Functional Requirements

### 2.1 Backend Chaos Exception Catching
*   **Target Scope**: Update `execute_streaming_loop` (and receiver/sender loops inside `web_server.py`) to actively catch socket exceptions, including `ConnectionResetError`, `asyncio.TimeoutError`, and `websockets.exceptions.ConnectionClosed`.
*   **Zero-Retry Bubble Principle**: In accordance with user preference, do not perform automatic reconnect retries. If a connection fails, it must fail immediately.
*   **Clean Session Teardown**: Upon exception interception, the state machine must:
    *   Set `self.is_active = False` on the `ActiveSession` coordinator.
    *   Cancel the active background `streaming_task` task.
    *   Reset pre-warmed connection caches to `None` to prevent stale socket reuse.

### 2.2 Frontend Status & Error Broadcast
*   **Live Error Propagation**: Immediately broadcast a JSON error message of type `"status"` with status `"disconnected"` or type `"error"` containing the connection failure details to both `/nurse` and `/patient` WebSocket clients:
    ```json
    {
      "type": "error",
      "message": "Connection error: Gemini Gateway Abnormal Closure (1006)"
    }
    ```
*   **Visual Status Transition**: Ensure that both dashboard headers receive this broadcast and immediately transition their pre-warm badges to grey/transparent (`Standby: Off`) or red to indicate the inactive call status.

### 2.3 Dependency Scaffolding for Future E2E
*   **Playwright & Selenium Setup**: Scaffold future-facing E2E testing framework packages (e.g., `playwright`, `pytest-playwright`) in `pyproject.toml` using `uv` to enable out-of-the-box browser-level testing for next phases.

---

## 3. Non-Functional Requirements
*   **Zero Server Side-Effects**: A connection drop on a single simultaneous call must never impact the overall stability of the FastAPI parent web server or affect separate connected HTTP clients.
*   **Zero Playhead Overlap**: Ensuring that when streaming fails, any active chunk-sending loops stop sending immediate subsequent frames to avoid data corruption if the session is manually re-started.

---

## 4. Acceptance Criteria
1.  **Headless Chaos Test Passing**: A new test `tests/test_chaos_recovery.py` runs and passes, simulating a mid-stream connection reset error and verifying that:
    *   The error event is sent to both client web sockets.
    *   The streaming task is cancelled cleanly.
    *   The session is reset to inactive.
2.  **Pytest Suite Cleanliness**: All 100 existing tests continue to pass 100% green on local runs.
3.  **Future Scaffolding Verified**: `pyproject.toml` is cleanly updated with testing dependencies without breaking existing virtual environments.
