# Track Specification: Customer Feedback & Strategic Advisory Enhancements

## 1. Overview
This track addresses key customer feedback items and delivers strategic advisory features for the **Project Dashboard (Future Defence Secret Environment / F-DSE)**:
1. **Program Terminology Update**: Update project heading and configuration from 'Federated Defence Secret Environment' to **'Future Defence Secret Environment'**.
2. **Persistent 'Google Need-to-Know' Module**: Add a prominent, persistent executive alert container at the very top of the dashboard visible across all tabs.
3. **'Looking Around the Corner' Advisory Insights**: Integrate predictive forward-looking advisory insights directly into the Executive Summary tab.
4. **Clean Register Separation**: Provide cleanly separated tabs for 'Internal Risks' (107 Joint Program risks) and 'Team Google Risks' (12 TG risks) with explicit labels and provenance tooltips.
5. **CD1 Driver Tree Direct Risk Modal Deep-Linking**: Enable clicking linked risks in the CD1 Driver Tree section to directly open full Risk Detail Modals.

---

## 2. Functional Requirements

### 2.1 Heading & Program Rebranding
- Update 'Federated Defence Secret Environment' in `data/f-dse/config.json`, header titles, report exports, and template fallbacks to **'Future Defence Secret Environment'** (F-DSE).

### 2.2 Global 'Google Need-to-Know' Header Module
- Add a top-level alert/briefing container above the primary navigation bar.
- Persistently render across all dashboard tabs (`exec-briefing`, `overview`, `team-google`, `issues`, `trends`, `blueprints`, `driver-tree`, `ledger`).
- Highlight critical Google-specific action items, upcoming contractual decisions, and urgent operational notices.
- Support collapsible state with memory.

### 2.3 'Looking Around the Corner' Forward Advisory Insights (Executive Summary)
- Add a dedicated predictive intelligence section to the Executive Summary tab (`#view-exec-briefing`).
- Synthesize impending delivery friction points, critical path lead times, upcoming contractual milestones (CD1 Horizon), unassigned/unactioned risks, and dependency traps.
- Surface prioritized actionable recommendations for executive decision-makers.

### 2.4 Dedicated & Clearly Separated Risk Tabs
- **Tab 2**: Clearly labelled **'Internal Risks'** with badge `(107)` representing the Joint Program / Internal Risk Register.
- **Tab 3**: Clearly labelled **'Team Google Risks'** with badge `(12)` and Google security shield icon representing the Team Google Register.
- Provide explicit subtitle and tooltip context clarifying the exact provenance and governance boundary of each register.

### 2.5 CD1 Driver Tree Direct Risk Modal Deep-Linking
- On deliverable cards in the CD1 Driver Tree tab:
  - When **1 risk** is linked: clicking the risk badge directly opens the complete Risk Detail Modal (`openRiskModal(riskId)`).
  - When **multiple risks** are linked: render discrete clickable risk chips (e.g., `Risk #27`, `Risk #42`) that open the specific risk modal upon click, alongside a filter action for the Risk Explorer.

---

## 3. Non-Functional & Architecture Requirements
- Zero-Server compatibility (runs entirely client-side with localStorage/Drive sync).
- Consistent Tailwind CSS styling and responsive layout across widescreen desktop and mobile devices.
- Unit and integration tests validating register isolation, heading rebranding, modal opening, and dynamic synthesis.

---

## 4. Acceptance Criteria
- [x] Header and default configuration show 'Future Defence Secret Environment'.
- [x] 'Google Need-to-Know' is persistently visible at the top across all tabs.
- [x] Executive Summary tab includes 'Looking Around the Corner' predictive insights.
- [x] Risk tabs are cleanly separated into 'Internal Risks (107)' and 'Team Google Risks (12)'.
- [x] Driver Tree deliverable risk links open specific risk detail modals directly.
