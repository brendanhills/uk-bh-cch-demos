// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Executive Briefing Module
// =============================================================================

import { store } from '../state.js';
import { cleanField, computeRiskKpis } from '../analytics.js';
import { openItemDetailModal } from './modals.js';

let isPlayingPodcast = false;
let podcastAudio = null;

export function renderExecBriefing() {
    const raw = store.get('rawData') || {};
    const config = store.get('config') || {};
    const risks = store.get('liveRisks') || [];
    const issues = store.get('liveIssues') || [];
    const kpis = computeRiskKpis(risks);

    // 1. Google Need-to-Know Badge
    const ntkBadge = document.getElementById('appNtkBadge');
    if (ntkBadge) {
        ntkBadge.innerText = `Google NTK • ${kpis.criticalCount} Critical Risks (${kpis.open} Active)`;
    }

    // 2. Cockpit KPI Cards
    const kpiCritical = document.getElementById('kpiCriticalRisks');
    if (kpiCritical) kpiCritical.innerText = kpis.criticalCount;

    const kpiOpen = document.getElementById('kpiOpenRisks');
    if (kpiOpen) kpiOpen.innerText = kpis.open;

    const kpiIssues = document.getElementById('kpiEscalatedIssues');
    if (kpiIssues) kpiIssues.innerText = issues.filter(i => i.status !== 'Closed').length;

    // 3. Top Critical Risks Table
    const topRisksContainer = document.getElementById('topCriticalRisksList');
    if (topRisksContainer) {
        const top5 = [...risks].sort((a, b) => (b.inherentScore || 0) - (a.inherentScore || 0)).slice(0, 5);
        let rHtml = '';
        top5.forEach((r, idx) => {
            rHtml += `
                <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td class="p-2.5 font-bold font-mono text-indigo-700">${r.id}</td>
                    <td class="p-2.5 font-semibold text-slate-800">${cleanField(r.riskName || r.title)}</td>
                    <td class="p-2.5 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-800">Score ${r.inherentScore || 'N/A'}</span></td>
                    <td class="p-2.5 text-right">
                        <button onclick="window.app.openItemDetailModal('risk', '${r.id}')" class="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-bold text-xs rounded-lg border border-indigo-200 cursor-pointer shadow-2xs">
                            Inspect ↗
                        </button>
                    </td>
                </tr>
            `;
        });
        topRisksContainer.innerHTML = rHtml;
    }

    // 4. Top Escalated Issues Table
    const topIssuesContainer = document.getElementById('topEscalatedIssuesList');
    if (topIssuesContainer) {
        const top5Issues = [...issues].slice(0, 5);
        let iHtml = '';
        top5Issues.forEach((i, idx) => {
            iHtml += `
                <tr class="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td class="p-2.5 font-bold font-mono text-amber-700">${i.id}</td>
                    <td class="p-2.5 font-semibold text-slate-800">${cleanField(i.issueName || i.title)}</td>
                    <td class="p-2.5 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900">${i.severity || 'Medium'}</span></td>
                    <td class="p-2.5 text-right">
                        <button onclick="window.app.openItemDetailModal('issue', '${i.id}')" class="px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-800 font-bold text-xs rounded-lg border border-amber-300 cursor-pointer shadow-2xs">
                            Inspect ↗
                        </button>
                    </td>
                </tr>
            `;
        });
        topIssuesContainer.innerHTML = iHtml;
    }
}

export function togglePodcast() {
    const btn = document.getElementById('btnPlayPodcast');
    const player = document.getElementById('podcastAudioPlayer');
    if (!player) return;

    if (player.paused) {
        player.play();
        if (btn) btn.innerHTML = '<span>⏸️</span><span>Pause Briefing</span>';
    } else {
        player.pause();
        if (btn) btn.innerHTML = '<span>▶️</span><span>Play Audio Briefing</span>';
    }
}

export function copyBriefingText() {
    const textEl = document.getElementById('geminiBriefingText') || document.getElementById('execBriefingContent');
    if (textEl) {
        navigator.clipboard.writeText(textEl.innerText).then(() => {
            alert('Briefing text copied to clipboard!');
        });
    }
}
