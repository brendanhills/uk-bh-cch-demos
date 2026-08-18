# Phased Bug Implementation Plan — Framework Simplification & Dashboard Stability

**Date:** `2026-08-18`  
**Target Strategy:** `Immediate Stability & Client-Side Data Normalization`  
**Objective:** Simplify the separation of data and dashboard framework by introducing universal client-side data normalization and robust fallbacks in `index.html`. This ensures that all dashboard tabs (Driver Tree, Blueprint Knowledge, Performance Trends, Executive Briefing, and Team Google) render reliably and completely regardless of minor schema variations or pre-computation cache status.

---

## 🎯 Architecture Simplification Strategy

Instead of relying on fragile, multi-layered pre-computation scripts that break when fields or files differ between projects:
1. **Universal Client-Side Normalization (`index.html`)**:
   - Normalize Driver Tree gates (`description`, `completeBy`, `progress`, `status`).
   - Normalize Risk & Issue models (`riskName || riskTitle || riskDescription`, `residualRiskScore || Likelihood × Consequence`).
   - Dynamically compute longitudinal trends and 5×5 matrix distributions directly in the browser if `precomputed_analytics.json` is absent or incomplete.
2. **Default Built-In Knowledge Catalog**:
   - Provide built-in fallback mapping for standard Solution Blueprints (Annexes A through L) so Blueprint Knowledge renders 100% of the time.
3. **Header Simplification (FR #66 & Bug #65)**:
   - Remove the redundant project dropdown menu, relying exclusively on `?project=<slug>` and `.env` default.
   - Enforce `flex-nowrap` on header action controls to permanently eliminate button wrapping.
4. **Natural Audio Speech Fallback (Bug #67)**:
   - Implement Web Speech Synthesis API (`window.speechSynthesis`) fallback to read the dual-host Gemini transcript aloud with natural spoken dialogue rather than playing synthetic chime tones.

---

## 📋 Phased Execution Roadmap

| Phase | Bug ID | Type | Priority | Impact | Risk | Summary & Strategy |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Phase 1** | **#61** | `Bug` | **P1** | High | Low | **Driver Tree Data Normalization**: Map `g.name || g.description` and `g.dueDate || g.completeBy` with calculated progress fallback. |
| **Phase 1** | **#62** | `Bug` | **P1** | High | Low | **Blueprint Knowledge Fallback**: Add default Solution Blueprints catalog (Annexes A-L) in `index.html` & `knowledge.json`. |
| **Phase 1** | **#63** | `Bug` | **P1** | High | Low | **Burndown Chart Resilience**: Normalize `inherentScores || inherentAvg` in `computeTimelineMetrics()` and add dynamic burndown calculation. |
| **Phase 1** | **#68** | `Bug` | **P1** | High | Low | **Top 5 Risks & Issues Resilience**: Add normalized name fallbacks and clean empty-state cards for Top 5 containers. |
| **Phase 1** | **#64** | `Bug` | **P2** | Medium | Low | **Team Google "All" Filter Reset**: Automatically reset `teamGoogleActiveMatrixCellFilter = null` upon clicking status buttons. |
| **Phase 1** | **#65 / #66** | `Bug/FR` | **P2** | Medium | Low | **Header Simplification**: Remove project dropdown; enforce `flex-nowrap` on header action bar. |
| **Phase 2** | **#67** | `Bug` | **P2** | Medium | Medium | **Spoken Dialogue Audio**: Add Web Speech Synthesis API browser playback for Gemini podcast dialogue (Alex & Jordan). |
| **Phase 2** | **#69** | `Bug` | **P3** | Low | Low | **Favicon Handler**: Add inline SVG favicon and server 200/204 response for `/favicon.ico`. |
| **Phase 2** | **#56** | `Bug` | **P1** | Medium | Low | **Multi-Sheet Header Links**: Support dynamic link mapping for Joint Program vs Team Google sheets. |
| **Phase 2** | **#53** | `Bug` | **P1** | Medium | Low | **Gap #1 Jump Navigation**: Add smooth scroll & highlight for Gap Close Plans. |
| **Phase 3** | **#60** | `FR` | **P2** | Medium | Low | **In-Dashboard Pipeline Triggers**: Add UI action triggers in Workspace Sync Modal. |
| **Phase 3** | **#57** | `Bug` | **P2** | Medium | Low | **Driver Tree Layout Compaction**: Compact card spacing when items lack shifts. |
| **Phase 3** | **#1** | `Bug` | **P2** | Medium | Medium | **Export File Generators**: Implement client-side PDF/PPTX export generators. |

---

## 🛠️ Phase 1 Implementation Details (Immediate Fixes)

### 1. Fix Bug #61: Driver Tree Normalization
- **File**: `index.html`
- **Change**: In the `capabilityDrops` parsing loop, map:
  ```javascript
  DRIVER_TREE_ITEMS.push({
      itemNumber: g.ref || g.itemNumber || '',
      description: g.description || g.name || g.title || 'Deliverable Gate',
      status: (g.status || cd.status || 'GREEN').toUpperCase(),
      level: g.level || 2,
      owner: g.owner || cd.lead || 'Workstream Lead',
      completeBy: g.completeBy || g.dueDate || g.targetDate || cd.targetDate || 'TBD',
      progress: g.progress !== undefined ? g.progress : (String(g.status).toUpperCase() === 'GREEN' ? 100 : (String(g.status).toUpperCase() === 'AMBER' ? 60 : 35)),
      shift: g.shift || null,
      gapCloseRef: g.gapCloseRef || null,
      gapCloseTitle: g.gapCloseTitle || ''
  });
  ```

### 2. Fix Bug #62: Blueprint Knowledge Default Mapping
- **File**: `index.html` & `data/f-dse/knowledge.json`
- **Change**: Define `DEFAULT_BLUEPRINTS` in `index.html` covering Annexes A–L so that if `BUNDLE_ANNEX_MAPPING` is empty, the dashboard defaults to full blueprint rendering.

### 3. Fix Bug #63: Burndown Timeline Resilience
- **File**: `index.html`
- **Change**: In `computeTimelineMetrics()`:
  ```javascript
  inherentScores: t.burndown?.inherentScores || t.burndown?.inherentAvg || defaultInherentSeries,
  residualScores: t.burndown?.residualScores || t.burndown?.residualAvg || defaultResidualSeries
  ```

### 4. Fix Bug #68: Top 5 Risks & Issues Normalization
- **File**: `index.html`
- **Change**: In `renderTop5Risks()` and `renderTop5Issues()`:
  - Normalize titles: `r.riskName || r.riskDescription || r.title || 'Risk'`.
  - Add fallback card: `<tr><td class="text-center py-6 text-slate-400 text-xs italic">No active critical items in current reporting cycle.</td></tr>`.

### 5. Fix Bug #64: Team Google "All" Filter Reset
- **File**: `index.html`
- **Change**: In `setTeamGoogleStatusFilter(status)`:
  - If `status === 'all'` or status changes, set `teamGoogleActiveMatrixCellFilter = null` and hide `#teamGoogleMatrixFilterNotice`.

### 6. Fix Bug #65 & FR #66: Header Simplification
- **File**: `index.html`
- **Change**: Remove the `#projectDropdownMenu` button and dropdown markup. Update the controls container to `flex items-center gap-2 flex-nowrap`.

---

## 🧪 Verification Plan

1. **Automated Unit Tests**:
   - `tests/test_phase1_stability.py`: Validates normalization of Driver Tree gates, Blueprint fallbacks, burndown score metrics, Top 5 titles, and header single-line layout.
   - Regression suite: Ensure all existing tests pass (`python3 -m unittest discover tests`).
2. **Visual & Browser Verification**:
   - Verify Project F-DSE (`http://uk-bh-cloudtop.c.googlers.com:9000/?project=f-dse`):
     - Driver Tree cards render title, completion %, and target dates cleanly.
     - Blueprint Knowledge displays all 10 Solution Blueprint cards.
     - Performance Trends plots Inherent vs Residual burndown lines across Weeks 22–27.
     - Executive Briefing Top 5 Critical Risks and Top 5 Escalated Issues populate with cards.
     - Header displays a clean, single-row action bar without wrapping.
