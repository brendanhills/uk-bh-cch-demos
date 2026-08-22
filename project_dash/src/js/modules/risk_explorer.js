// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Risk Explorer Cards & Filters
// =============================================================================

import { store } from '../state.js';
import { cleanField, filterRisksByStatus, filterRisksByCell, getScoreBadgeClass } from '../analytics.js';
import { openItemDetailModal } from './modals.js';

export function renderRiskExplorer() {
    const container = document.getElementById('explorerList') || document.getElementById('riskCardsContainer');
    if (!container) return;

    const risks = store.get('liveRisks') || [];
    const ratingType = store.get('matrixRating') || 'inherent';
    const statusFilter = store.get('matrixStatus') || 'open';
    const activeCell = store.get('activeMatrixCellFilter');
    const search = (store.get('searchQuery') || '').toLowerCase();
    const catFilter = store.get('filterCategory') || 'all';

    let list = filterRisksByStatus(risks, statusFilter);
    if (activeCell) {
        list = filterRisksByCell(list, activeCell.l, activeCell.c, ratingType);
    }
    if (search) {
        list = list.filter(r => (r.riskName || '').toLowerCase().includes(search) || (r.id || '').toLowerCase().includes(search));
    }
    if (catFilter !== 'all') {
        list = list.filter(r => (r.category || '').toLowerCase() === catFilter.toLowerCase());
    }

    const countEl = document.getElementById('explorerMatchCount');
    if (countEl) countEl.innerText = `${list.length} Risks Displayed`;

    let html = '';
    for (const r of list) {
        const score = ratingType === 'inherent' ? (r.inherentScore || 'N/A') : (r.residualScore || 'N/A');
        const badgeClass = getScoreBadgeClass(score);

        html += `
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:shadow-xs transition-all space-y-2.5">
                <div class="flex items-center justify-between gap-3">
                    <div class="flex items-center gap-2">
                        <span class="font-mono font-extrabold text-indigo-700 text-xs">${r.id}</span>
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${badgeClass}">Score: ${score}</span>
                        <span class="bg-slate-100 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-full">${r.status || 'Active'}</span>
                    </div>
                    <button onclick="window.app.openItemDetailModal('risk', '${r.id}')" class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs rounded-lg border border-indigo-200 cursor-pointer shadow-2xs">
                        Inspect ↗
                    </button>
                </div>
                <h4 class="text-xs sm:text-sm font-extrabold text-slate-900">${cleanField(r.riskName || r.title)}</h4>
                <div class="flex items-center gap-4 text-[11px] text-slate-500">
                    <span>👤 ${cleanField(r.owner || r.riskOwner)}</span>
                    <span>📁 ${cleanField(r.category)}</span>
                    <span>🎯 Ref ${cleanField(r.driverTreeRef || r.driverRef)}</span>
                </div>
            </div>
        `;
    }

    container.innerHTML = html || '<div class="p-8 text-center text-slate-400 font-medium">No matching risks found.</div>';
}
