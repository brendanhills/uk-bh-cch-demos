# CI/CD Deployment & Build Workflow Rules

- **Asynchronous Push Execution (Non-Blocking Invariant)**:
  * Pushing to Git (`origin dev`) triggers an automated Google Cloud Build job in the background.
  * **DO NOT** block execution, set arbitrary sleep timers, or poll in a loop waiting for Cloud Build to complete after every push.
  * Report the successful push immediately, provide the Cloud Build console link, and proceed with subsequent work.

- **Skipping Builds for Documentation-Only Commits (`[skip ci]`)**:
  * When committing updates that only affect documentation, guides, AI rules, specs, or session resumes:
    * Always append `[skip ci]` to the commit message:
      ```bash
      git commit -m "docs: update operations guide [skip ci]"
      ```
    * Cloud Build natively ignores commits containing `[skip ci]` or `[ci skip]`, preventing redundant builds.
  * **Path Filtering**: Triggers also exclude `project_dash/**/*.md`, `project_dash/docs/**`, `project_dash/.agents/**`, and `project_dash/conductor/**`.

- **Production Release Protocol (Tags on `dev`)**:
  * All development remains on the `dev` branch.
  * Production releases in Sydney (`australia-southeast1`) are triggered by pushing release tags matching `^project_dash/prod-.*$`:
    ```bash
    git tag project_dash/prod-v1.0.0
    git push origin project_dash/prod-v1.0.0
    ```

- **On-Demand Build Status & Diagnostics Verification**:
  * When explicitly asked to check build status or diagnose a failure, execute:
    ```bash
    python3 scripts/check_build_status.py --env dev
    python3 scripts/check_build_status.py --env prod
    ```
  * For checking recent history: `python3 scripts/check_build_status.py --limit 5`
  * For inspecting a specific build ID: `python3 scripts/check_build_status.py --build-id <BUILD_ID>`
  * The script automatically parses pipeline steps, highlights exit codes, and extracts tail failure logs if a build fails.
