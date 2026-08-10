# Demo Storytelling & Disruption UI Rules

1. **Comparison Phase Default State**:
   - In 3-Phase or Before/After storytelling dashboards, navigating to the comparison/evolved phase MUST load the Baseline schedule initially.
   - Do NOT automatically overwrite the view with evolved code until the presenter clicks the explicit execution button (e.g. `Evolve Schedule`).

2. **Disruption Injection Rules**:
   - Interactive disruption triggers (`Simulate Disruption`, `Simulate Maintenance`) MUST target the active day/time window currently viewed on screen.
   - Surgeries overlapping with maintenance closures MUST be removed from the closed window and relocated to non-overlapping open slots.
   - Overlap validation MUST check against all active unavailability and maintenance events.
