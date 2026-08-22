// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Time Machine Controller
// =============================================================================

import { store } from '../state.js';
import { cleanField } from '../analytics.js';

export function getLatestWeekKey() {
    const snaps = store.get('timeMachineSnapshots') || {};
    const keys = Object.keys(snaps);
    return keys.length > 0 ? keys[keys.length - 1] : 'w27';
}

export function activateTimeMachine(weekKey) {
    const snaps = store.get('timeMachineSnapshots') || {};
    const snap = snaps[weekKey];
    if (!snap) return;

    store.set({
        activeTimeMachineWeek: weekKey,
        liveRisks: snap.risks || snap.masterRiskRegister || store.get('liveRisks'),
        liveIssues: snap.issues || snap.issueRegister || store.get('liveIssues')
    });

    const banner = document.getElementById('timeMachineBanner');
    const bannerWeek = document.getElementById('timeMachineBannerWeek');
    const weekLabel = snap.week || snap.weekLabel || ('Week ' + (snap.weekNumber || ''));

    if (weekKey === getLatestWeekKey()) {
        if (banner) banner.classList.add('hidden');
    } else {
        if (banner) banner.classList.remove('hidden');
        if (bannerWeek) bannerWeek.innerText = `${weekLabel} (${snap.date || ''})`;
    }

    const liveBadge = document.getElementById('liveStatusBadge');
    if (liveBadge) {
        liveBadge.innerText = `${weekLabel} ${weekKey === getLatestWeekKey() ? '(Live)' : '(Historical)'}`;
    }
}

export function returnToPresent() {
    activateTimeMachine(getLatestWeekKey());
}

export function toggleTimeMachineModal() {
    const modal = document.getElementById('timeMachineModal');
    if (!modal) return;
    if (modal.classList.contains('hidden')) {
        renderTimeMachineModalList();
        modal.classList.remove('hidden');
    } else {
        modal.classList.add('hidden');
    }
}

export function renderTimeMachineModalList() {
    const listEl = document.getElementById('timeMachineSnapshotsList');
    if (!listEl) return;

    const snaps = store.get('timeMachineSnapshots') || {};
    const activeWeek = store.get('activeTimeMachineWeek');
    const latestKey = getLatestWeekKey();

    let html = '';
    const sortedKeys = Object.keys(snaps).reverse();

    for (const k of sortedKeys) {
        const s = snaps[k];
        const label = s.week || s.weekLabel || ('Week ' + (s.weekNumber || ''));
        const isCurrent = k === activeWeek || (activeWeek === 'present' && k === latestKey);

        html += `
            <div onclick="window.app.activateTimeMachine('${k}'); window.app.toggleTimeMachineModal();" class="p-3 rounded-xl border ${isCurrent ? 'border-indigo-600 bg-indigo-50/70 shadow-xs ring-2 ring-indigo-500/20' : 'border-slate-200 bg-white hover:bg-slate-50'} flex items-center justify-between cursor-pointer transition-all">
                <div class="flex items-center gap-3">
                    <span class="text-xl">${isCurrent ? '⚡' : '📅'}</span>
                    <div>
                        <div class="text-sm font-extrabold text-slate-900">${label} <span class="text-xs text-slate-500 font-normal">(${s.date || 'Historical'})</span></div>
                        <div class="text-xs text-slate-500 font-medium">${(s.risks || []).length || s.totalRisks || 0} Risks Recorded • ${s.reportTitle || 'Weekly Pack'}</div>
                    </div>
                </div>
                <div class="text-right">
                    ${isCurrent ? '<span class="bg-indigo-600 text-white font-extrabold text-[10px] px-2.5 py-1 rounded-full uppercase tracking-wider">Active</span>' : '<span class="text-xs text-indigo-600 font-bold hover:underline">Travel →</span>'}
                </div>
            </div>
        `;
    }

    listEl.innerHTML = html;
}
