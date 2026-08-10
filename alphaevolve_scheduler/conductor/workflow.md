# Project Workflow

## Guiding Principles
1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`.
2. **Visual & Fast Iteration:** Focus on building the visual PoC and AlphaEvolve integration.
3. **Manual Verification:** Verify changes visually in the UI or via script execution.
4. **Best Effort Testing:** Automated tests are optional and focused only on core evaluator logic if needed.
5. **Lightweight Task Management:** Streamline tracking to avoid agent and context overhead.

## Task Workflow

### Standard Task Workflow
1. Select the next task from `plan.md`.
2. Mark it in progress `[~]`.
3. Implement the feature or algorithm changes.
4. Visually or manually verify that it works as expected.
5. Commit the changes with a clear message.
6. Mark the task complete `[x]` in `plan.md`.

### Phase Completion Verification and Checkpointing Protocol
1. **Visual/Manual Approval:** Announce to the user that the phase is complete.
2. **Demonstration:** Show the working UI or script execution in the chat, or provide instructions for the user to run it.
3. **User Confirmation:** Get a quick "yes" or feedback from the user.
4. **Checkpoint Commit:** Commit the final state and tag the phase as complete in `plan.md`.

## Quality Gates
Before marking any task complete, verify:
- [ ] Feature works visually and logically as specified.
- [ ] No syntax or runtime errors.
- [ ] Code follows project's code style guidelines.
- [ ] Working implementation is demonstrated to the user.

## Development Commands
### Setup
```bash
# Create venv and install dependencies
uv venv .venv && source .venv/bin/activate
uv pip install -p .venv/bin/python git+https://github.com/Google-Cloud-AI/alphaevolve-on-googlecloud.git python-dotenv nest_asyncio numpy
```

### Daily Development
```bash
# Start the static file server for the UI
./serve.sh
```

## Testing Requirements
- **Unit Testing:** Optional. Best effort for complex scheduling and mathematical logic in the evaluator.
- **Integration & UI Testing:** Strictly manual and visual (running the demo and checking the UI).

## Code Review Process
- Keep things simple and maintainable.
- Ensure the "Wow" factor and visual clarity are maintained.

## Commit Guidelines
### Message Format
```
<type>(<scope>): <description>
```
Standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `chore`.

## Definition of Done
A task is complete when it is implemented, visually verified, and working as demonstrated.

## Emergency Procedures
Fix it forward. Ensure the Demo works seamlessly.

## Deployment Workflow
Not applicable for this Phase 1 PoC. The "deployment" is running the local server and presenting the UI.

## Continuous Improvement
Optimize for speed, simplicity, and visual impact.
