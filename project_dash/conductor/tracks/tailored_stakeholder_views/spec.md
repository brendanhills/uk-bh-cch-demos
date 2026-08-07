# Specification: Tailored Stakeholder Views (Exec, PM, and Tech URL-Driven Views)

## 1. Overview & Objective
Provide tailored, role-customized dashboard experiences for distinct project stakeholders without cluttering the primary user interface. All role-specific views are driven cleanly via shareable URL query parameters (`?view=exec`, `?view=pm`, `?view=tech`), defaulting to the unified single-view dashboard when unparameterized (`/`).

---

## 2. Core Architectural Invariants
- **Zero UI Pollution**: No mode switcher pills or role selectors in the header. The UI stays 100% clean.
- **URL-Driven Routing**:
  - **Default (`/`)**: Universal 4-tab hybrid view serving both PMs and Execs.
  - **`?view=exec` (Executive Decision View)**: Deep-dive executive decision cockpit, Top 3 actions, 4-pillar KPI strip, and Neural Australian Audio Briefing.
  - **`?view=pm` (PM Governance & Ledger View)**: Operational view exposing Tab 5 (`📋 Whole Register Ledger`) with full risk/issue tables, mitigation tracking, and milestone alignment. Audio player is hidden.
  - **`?view=tech` (Technical Architecture & ATO View)**: Engineering & security view prioritizing the CD1 Driver Tree, ATO-C Gate readiness, and technical blocker paths. Audio player is hidden.
- **Deep AI Content Adaptation**: Dedicated Gemini 3.5 Pro prompt synthesis templates tailored for each specific view role.

---

## 3. Functional Requirements
1. **URL Parameter Parser**: Parse `window.location.search` for `view` parameter on load and route view configuration.
2. **Role-Tailored AI Briefings**:
   - `exec`: 90-second executive decision & intervention synthesis.
   - `pm`: Delivery velocity, gate slippage, and mitigation progress synthesis.
   - `tech`: Security architecture, ATO-C gates, and technical blocker breakdown.
3. **Role-Tailored Layouts**:
   - Dynamic tab visibility and custom default tabs per view.
   - Audio briefing player rendered only on `?view=exec` and default view.
