# Specification: Executive Summary Briefing Module (v2)

## 1. Overview & Purpose
This specification defines the enhanced **Executive Summary Briefing Module** for the F-DSE Program. Built directly from customer meeting feedback, it replaces static/bare summaries with a high-density executive briefing view tailored for leadership meetings, risk committees, and customer status reviews.

---

## 2. Customer Functional Requirements
The module directly implements the following 7 executive requirements:

1. **Top 5 Issues & Top 5 Risks:** Ranked by criticality with severity badges, residual ratings, and key drivers.
2. **Top 5 Next Actions:** High-priority immediate action plans and mitigation owners.
3. **What's Burning Panel:** Red-alert items requiring immediate executive intervention or resolution.
4. **Briefing-to-Briefing Delta Tracker:** Track changes since the last executive briefing date (configurable baseline date, e.g., Last Briefing Date vs Current Date).
5. **Executive Focus & Escalation Help Needed:** Highlighted callouts specifying required executive sign-offs, resource requests, and PSG/IPF/Internal escalation assistance.
6. **Trending Towards Bad/Good Radar:** Directional trend indicators (`Better ↑`, `Worse ↓`, `Same ↔`), featuring a dedicated **"Trending Bad Radar"** for items currently rated Low/Medium but escalating towards High/Critical.
7. **Dual-Platform Availability:** Implemented across both Streamlit (`app.py`/`app_phase2.py`) and AI Studio Web Application (`index.html`).

---

## 3. Architecture & User Interface Mapping

### 3.1. Executive Briefing Header
- **Briefing Date Selector:** Baseline comparison selector (e.g. `29 Jul 2026 (Last Briefing)` vs `Current`).
- **Program Health & Trajectory Badge:** Visual status badge (`Red 🔴`, `Amber 🟡`, `Green 🟢`).

### 3.2. Top 5 Items & Top 5 Actions
- **Top 5 Risks Table:** Ranked by Residual Risk Rating with Trend direction.
- **Top 5 Issues Table:** Ranked by Severity Rating with linked Action Plans.
- **Top 5 Next Actions Card Grid:** Next action items, owners, target completion dates, and status.

### 3.3. "What's Burning" & Escalations Panel
- **Red Alert "What's Burning" Banner:** Immediate critical blockers (e.g., E01 build quality, export control staffing).
- **Executive Help Needed Card:** Clear callouts detailing specific actions required from executive leadership.

### 3.4. Trending Radar & Delta Tracker
- **Trending Bad Radar:** Filtered list of items starting at Low/Medium consequence/likelihood that exhibit `Worse ↓` trends.
- **Briefing Delta Summary:** New items raised, closed items, and rating changes since selected baseline date.

---

## 4. Technology Stack & Alignment
- **Streamlit:** Python (`app.py`, `app_phase2.py`) using Pandas, Altair, and Streamlit containers/columns.
- **AI Studio Web App:** HTML5/Tailwind CSS single-page web app (`index.html`) with interactive JS tab views.

---

## 5. Acceptance Criteria
- [ ] Top 5 Risks, Top 5 Issues, and Top 5 Next Actions render accurately.
- [ ] "What's Burning" banner highlights critical red-alert blockers.
- [ ] Executive Help Needed section specifies escalation requirements.
- [ ] Trending Bad Radar identifies items escalating from Low/Medium to High/Critical.
- [ ] Briefing Delta compares metrics against selected baseline briefing date.
- [ ] Available in both Streamlit and AI Studio `index.html`.
