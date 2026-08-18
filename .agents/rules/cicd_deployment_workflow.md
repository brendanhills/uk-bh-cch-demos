# CI/CD Deployment & Build Workflow Rules

- **Asynchronous Push Execution (Non-Blocking Invariant)**:
  * Pushing to Git (`origin dev` or `origin main`) triggers an automated Google Cloud Build job in the background.
  * **DO NOT** block execution, set arbitrary sleep timers, or poll in a loop waiting for Cloud Build to complete after every push.
  * Report the successful push immediately, provide the Cloud Build console link, and proceed with subsequent work.

- **On-Demand Build Status & Diagnostics Verification**:
  * When explicitly asked to check build status or diagnose a failure, execute:
    ```bash
    python3 scripts/check_build_status.py
    ```
  * For checking recent history: `python3 scripts/check_build_status.py --limit 5`
  * For inspecting a specific build ID: `python3 scripts/check_build_status.py --build-id <BUILD_ID>`
  * The script automatically parses pipeline steps, highlights exit codes, and extracts tail failure logs if a build fails.
