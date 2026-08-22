// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Issue Register Ledger Table
// =============================================================================

import { store } from '../state.js';
import { cleanField } from '../analytics.js';
import { openItemDetailModal } from './modals.js';

export function renderIssueTable() {
    const tbody = document.getElementById('issueTableBody');
    if (!tbody) return;

    const issues = store.get('liveIssues') || [];
    let html = '';

    for (const i of issues) {
        const sevClass = i.severity === 'High' ? 'bg-red-100 text-red-800' : (i.severity === 'Medium' ? 'bg-amber-100 text-amber-900' : 'bg-slate-100 text-slate-700');

        html += `
            <tr class="border-b border-slate-100 hover:bg-slate-50 text-xs">
                <td class="p-3 font-mono font-bold text-amber-700">${i.id}</td>
                <td class="p-3 font-bold text-slate-800">${cleanField(i.issueName || i.title)}</td>
                <td class="p-3 text-center"><span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${sevClass}">${i.severity || 'Medium'}</span></td>
                <td class="p-3 text-slate-600">${cleanField(i.owner || i.issueOwner)}</td>
                <td class="p-3 text-slate-600 font-mono">${cleanField(i.driverTreeRef || i.driverRef)}</td>
                <td class="p-3 text-slate-700 max-w-xs truncate">${cleanField(i.actionPlan || i.mitigation)}</td>
                <td class="p-3 text-right">
                    <button onclick="window.app.openItemDetailModal('issue', '${i.id}')" class="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 font-bold text-xs rounded-lg border border-amber-300 cursor-pointer shadow-2xs">
                        Inspect ↗
                    </button>
                </td>
            </tr>
        `;
    }

    tbody.innerHTML = html;
}
