// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Universal Modals Manager
// =============================================================================

import { store } from '../state.js';
import { cleanField, calculateMatrixScore, getScoreBadgeClass } from '../analytics.js';

export function openItemDetailModal(type, id) {
    const modal = document.getElementById('itemDetailModal');
    if (!modal) return;

    const isRisk = type === 'risk';
    const risks = store.get('liveRisks') || [];
    const tgRisks = store.get('teamGoogleRisks') || [];
    const issues = store.get('liveIssues') || [];

    const item = isRisk ? (risks.find(r => r.id === id) || tgRisks.find(r => r.id === id)) : issues.find(i => i.id === id);
    if (!item) return;

    const titleEl = document.getElementById('detailModalTitle');
    const badgeEl = document.getElementById('detailModalBadge');
    const bodyEl = document.getElementById('detailModalBody');

    if (titleEl) titleEl.innerText = isRisk ? `${item.id}: ${item.riskName || item.title || 'Risk Detail'}` : `${item.id}: ${item.issueName || item.title || 'Issue Detail'}`;
    if (badgeEl) {
        badgeEl.innerText = isRisk ? `Risk • ${item.status || 'Active'}` : `Issue • ${item.status || 'Active'}`;
        badgeEl.className = isRisk ? 'bg-indigo-100 text-indigo-800 text-xs font-bold px-2.5 py-1 rounded-full' : 'bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-full';
    }

    if (bodyEl) {
        bodyEl.innerHTML = `
            <div class="space-y-4 text-xs">
                <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                    <h4 class="font-extrabold text-slate-800 text-sm mb-1">Description & Statement</h4>
                    <p class="text-slate-700 leading-relaxed">${cleanField(item.description || item.riskName || item.issueName)}</p>
                </div>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200"><span class="text-slate-400 block">Owner</span><strong class="text-slate-900 font-bold">${cleanField(item.owner || item.riskOwner || item.issueOwner)}</strong></div>
                    <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200"><span class="text-slate-400 block">Category</span><strong class="text-slate-900 font-bold">${cleanField(item.category || item.issueCategory)}</strong></div>
                    <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200"><span class="text-slate-400 block">Driver Ref</span><strong class="text-indigo-700 font-mono font-bold">${cleanField(item.driverTreeRef || item.driverRef)}</strong></div>
                    <div class="p-2.5 bg-slate-50 rounded-lg border border-slate-200"><span class="text-slate-400 block">Status</span><strong class="text-slate-900 font-bold">${cleanField(item.status)}</strong></div>
                </div>
                ${item.mitigation || item.actionPlan || item.treatmentPlan ? `
                    <div class="bg-emerald-50/60 p-3.5 rounded-xl border border-emerald-200">
                        <h4 class="font-extrabold text-emerald-900 text-sm mb-1">Remediation / Treatment Plan</h4>
                        <p class="text-emerald-950 leading-relaxed">${cleanField(item.mitigation || item.actionPlan || item.treatmentPlan)}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    modal.classList.remove('hidden');
}

export function closeItemDetailModal() {
    const modal = document.getElementById('itemDetailModal');
    if (modal) modal.classList.add('hidden');
}

export function openWorkspaceSyncModal() {
    const modal = document.getElementById('sheetsModal');
    if (modal) modal.classList.remove('hidden');
}

export function closeWorkspaceSyncModal() {
    const modal = document.getElementById('sheetsModal');
    if (modal) modal.classList.add('hidden');
}

export function showToast(message, isSuccess = true) {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-xl shadow-lg font-bold text-xs flex items-center gap-2 transition-all transform translate-y-2 animate-bounce ${isSuccess ? 'bg-slate-900 text-white border border-slate-700' : 'bg-red-600 text-white'}`;
    toast.innerHTML = `<span>${isSuccess ? '✅' : '⚠️'}</span><span>${message}</span>`;
    document.body.appendChild(toast);
    setTimeout(() => { toast.remove(); }, 3500);
}
