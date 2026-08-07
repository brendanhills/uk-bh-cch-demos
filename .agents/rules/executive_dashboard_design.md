# Executive Dashboard & Exception-First Reporting Rule

## Core Philosophy: "No News is Good News"
An executive dashboard is not an exhaustive encyclopedia; it is a **decision-support and intervention cockpit**. Executives should never have to sift through pages of status updates to identify what matters.

## Key Design & Communication Invariants:

1. **Explicit "Ask for Help" Signaling**:
   - If an issue, risk, or gate is escalated to the Executive Summary, it **must explicitly articulate the specific ask** (e.g., *"Joint Executive Board Decision Required: Approve CD1.5 SRR glide path"* or *"Action Needed: Intervene with Cth for Milestone 1 acceptance"*).
   - Answer the 3 Executive Questions immediately:
     1. **What is broken / at risk?** (Technical & Financial exposure)
     2. **Why can't the working group solve it?** (Blocker rationale)
     3. **What specific decision or help is needed from leadership?** (Clear action item)

2. **1-Cycle Blocker Resolution Protocol (Closing the Loop)**:
   - When a critical red blocker or escalation is resolved, **present it prominently for exactly 1 reporting cycle** under a dedicated "✅ Resolved This Cycle" banner.
   - This provides closure for leadership ("The blocker you were briefed on is now solved") without contaminating the open intervention queue.
   - In subsequent reporting cycles, archive the item to the historical ledger ("No news is good news").

3. **Visual Hierarchy of Criticality & Progressive Disclosure**:
   - Open escalations requiring intervention MUST dominate the top-level visual hierarchy.
   - Cap active grid cards to the **Top 4–6 Critical Exceptions** with a 1-click `[View All (N) Plans]` progressive disclosure expander to prevent alarm fatigue.

4. **Cost, Schedule & Legal Risk Visibility**:
   - Always quantify the consequence if no action is taken (e.g., "+4 week delay", "contract variation required", "budget overrun").

5. **1-Minute Scannability & Dynamic Temporal Awareness**:
   - Surface the **top 1–2 critical decision points within the first 15 seconds**.
   - Dynamically evaluate deliverable dates against current real-time system time to automatically detect and flag overdue targets.

6. **Preservation of Reference Implementations (`dash_v1`)**:
   - The `project_dash/dash_v1/` directory contains the foundational reference prototype and baseline components.
   - **Invariant**: Never delete, purge, or modify `project_dash/dash_v1/` during refactoring, workspace cleanup, or dead-code elimination passes. Treat it as an immutable reference benchmark for feature parity and component comparisons.
