// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Blueprint Knowledge Base
// =============================================================================

import { store } from '../state.js';
import { cleanField } from '../analytics.js';

export function renderBlueprintKnowledge() {
    const container = document.getElementById('blueprintCardsContainer') || document.getElementById('blueprintsList');
    if (!container) return;

    const blueprints = store.get('blueprints') || [];
    let html = '';

    for (const b of blueprints) {
        html += `
            <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2">
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-indigo-700">${b.id || 'Blueprint'}</span>
                    <span class="text-[10px] bg-indigo-50 text-indigo-800 font-bold px-2 py-0.5 rounded">${b.annex || 'Annex Reference'}</span>
                </div>
                <h4 class="font-extrabold text-slate-900 text-sm">${cleanField(b.title || b.name)}</h4>
                <p class="text-xs text-slate-600">${cleanField(b.description || b.summary)}</p>
            </div>
        `;
    }

    container.innerHTML = html;
}
