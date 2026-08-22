// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — 5x5 Heatmap Renderers
// =============================================================================

import { store } from '../state.js';
import {
    MATRIX_SCORES_TABLE,
    CONSEQUENCE_NAMES,
    filterRisksByStatus,
    filterRisksByCell,
    calculateMatrixScore
} from '../analytics.js';

export function renderRiskHeatmap() {
    const risks = store.get('liveRisks') || [];
    const ratingType = store.get('matrixRating') || 'inherent';
    const statusFilter = store.get('matrixStatus') || 'open';
    const activeCell = store.get('activeMatrixCellFilter');

    const filteredRisks = filterRisksByStatus(risks, statusFilter);
    const container = document.getElementById('heatmapGridContainer');
    if (!container) return;

    let html = `
        <div class="grid grid-cols-6 gap-2.5 mb-2.5 text-xs font-bold text-slate-600 text-center uppercase tracking-wider">
            <div class="text-left font-extrabold text-slate-800 normal-case">Consequence (Y) ↓ / Likelihood (X) →</div>
            <div>1 Rare</div><div>2 Improbable</div><div>3 Occasional</div><div>4 Probable</div><div>5 Almost Certain</div>
        </div>
    `;

    for (let cIdx = 0; cIdx < 5; cIdx++) {
        const consequenceVal = 5 - cIdx;
        const cName = CONSEQUENCE_NAMES[cIdx];
        html += `<div class="grid grid-cols-6 gap-2.5 mb-2.5 items-center">`;
        html += `<div class="text-xs font-bold text-slate-800">${cName}</div>`;

        for (let lIdx = 0; lIdx < 5; lIdx++) {
            const likelihoodVal = lIdx + 1;
            const score = MATRIX_SCORES_TABLE[cIdx][lIdx];
            const cellRisks = filterRisksByCell(filteredRisks, likelihoodVal, consequenceVal, ratingType);

            let bgClass = 'bg-[#93c47d] text-slate-900';
            if (score >= 23) bgClass = 'bg-[#ea4335] text-white';
            else if (score >= 18) bgClass = 'bg-[#ff9900] text-white';
            else if (score >= 13) bgClass = 'bg-[#fdfdb9] text-amber-950 font-medium';
            else if (score >= 7) bgClass = 'bg-[#34a853] text-white';

            const isCellActive = activeCell && activeCell.l === likelihoodVal && activeCell.c === consequenceVal;
            const ringClass = isCellActive ? 'ring-4 ring-indigo-600 ring-offset-1 scale-105 z-20 shadow-md' : '';

            html += `
                <div onclick="window.app.highlightHeatmapCell(${likelihoodVal}, ${consequenceVal}, ${score})" class="hm-cell ${bgClass} ${ringClass} p-3.5 rounded-xl text-center font-bold text-sm flex items-center justify-center cursor-pointer select-none">
                    ${score}
                    ${cellRisks.length > 0 ? `<span class="hm-circle">${cellRisks.length}</span>` : ''}
                </div>
            `;
        }
        html += `</div>`;
    }

    container.innerHTML = html;
}

export function setMatrixRating(rating) {
    store.set({ matrixRating: rating });
    renderRiskHeatmap();
}

export function setMatrixStatus(status) {
    store.set({ matrixStatus: status });
    renderRiskHeatmap();
}

export function highlightHeatmapCell(l, c, score) {
    const active = store.get('activeMatrixCellFilter');
    if (active && active.l === l && active.c === c) {
        clearActiveCellFilter();
        return;
    }
    store.set({ activeMatrixCellFilter: { l, c, score } });
    renderRiskHeatmap();
    if (window.app && window.app.renderRiskExplorer) window.app.renderRiskExplorer();
}

export function clearActiveCellFilter() {
    store.set({ activeMatrixCellFilter: null });
    renderRiskHeatmap();
    if (window.app && window.app.renderRiskExplorer) window.app.renderRiskExplorer();
}
