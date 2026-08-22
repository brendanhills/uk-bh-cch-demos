// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Milestone 2 Driver Tree
// =============================================================================

import { store } from '../state.js';
import { cleanField } from '../analytics.js';

export function renderDriverTree() {
    const container = document.getElementById('driverTreeContainer');
    if (!container) return;

    const gates = store.get('driverTree') || [];
    let html = '';

    for (const g of gates) {
        html += `
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                <div class="flex items-center justify-between">
                    <span class="font-mono font-bold text-indigo-700 text-xs">${g.ref || 'Ref'}</span>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded ${g.status === 'Green' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">${g.status || 'Active'}</span>
                </div>
                <h4 class="font-extrabold text-slate-900 text-sm">${cleanField(g.title || g.name)}</h4>
                <p class="text-xs text-slate-600">${cleanField(g.description)}</p>
            </div>
        `;
    }

    container.innerHTML = html;
}
