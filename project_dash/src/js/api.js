// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Backend API & Sync Client
// Google Standards Compliant (go/tsstyle, go/js-practices)
// =============================================================================

import { store } from './state.js';

/**
 * Loads project configuration, snapshots, and raw dataset for the active project slug.
 * @param {string} projectSlug ('sample' or 'f-dse')
 * @returns {Promise<Object>} Loaded project payload
 */
export async function loadProjectData(projectSlug = 'sample') {
    const slug = projectSlug || 'sample';
    const basePath = `data/${slug}`;

    try {
        const [configRes, risksRes, issuesRes, snapshotsRes, knowledgeRes, driverTreeRes] = await Promise.allSettled([
            fetch(`${basePath}/config.json`),
            fetch(`${basePath}/risks.json`),
            fetch(`${basePath}/issues.json`),
            fetch(`${basePath}/snapshots.json`),
            fetch(`${basePath}/knowledge.json`),
            fetch(`${basePath}/driver_tree.json`)
        ]);

        const config = configRes.status === 'fulfilled' && configRes.value.ok ? await configRes.value.json() : null;
        const allRisks = risksRes.status === 'fulfilled' && risksRes.value.ok ? await risksRes.value.json() : [];
        const liveIssues = issuesRes.status === 'fulfilled' && issuesRes.value.ok ? await issuesRes.value.json() : [];
        const snapshotsData = snapshotsRes.status === 'fulfilled' && snapshotsRes.value.ok ? await snapshotsRes.value.json() : {};
        const knowledgeData = knowledgeRes.status === 'fulfilled' && knowledgeRes.value.ok ? await knowledgeRes.value.json() : {};
        const driverTree = driverTreeRes.status === 'fulfilled' && driverTreeRes.value.ok ? await driverTreeRes.value.json() : [];

        // Separate joint program risks and team google risks
        const jointRisks = allRisks.filter(r => !(r.sourceRegister === 'team_google' || r.sourceRegister === 'teamGoogle' || String(r.id).startsWith('TG-') || String(r.id).startsWith('AUR-TG-')));
        const teamGoogleRisks = allRisks.filter(r => (r.sourceRegister === 'team_google' || r.sourceRegister === 'teamGoogle' || String(r.id).startsWith('TG-') || String(r.id).startsWith('AUR-TG-')));

        const rawData = {
            risks: jointRisks,
            teamGoogleRisks,
            issues: liveIssues,
            snapshots: snapshotsData.snapshots || snapshotsData,
            knowledge: knowledgeData,
            driverTree
        };

        store.set({
            projectSlug: slug,
            config,
            rawData,
            liveRisks: jointRisks,
            liveIssues,
            teamGoogleRisks,
            blueprints: knowledgeData.sources || [],
            driverTree,
            timeMachineSnapshots: snapshotsData.snapshots || snapshotsData
        });

        return { config, rawData, snapshots: snapshotsData, risks: jointRisks, issues: liveIssues, teamGoogleRisks };
    } catch (err) {
        console.error('[API] Failed to load project data for ' + slug + ':', err);
        throw err;
    }
}

/**
 * Triggers backend Google Drive & Sheets synchronization.
 * @param {string} projectSlug 
 * @returns {Promise<Object>}
 */
export async function syncGoogleSheet(projectSlug = 'sample') {
    const slug = projectSlug || store.get('projectSlug') || 'sample';
    try {
        const res = await fetch(`/api/sync-sheet?project=${slug}`, { method: 'POST' });
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        const data = await res.json();
        return data;
    } catch (err) {
        console.warn('[API] Sync sheet fallback to local data:', err);
        return { status: 'fallback', message: err.message };
    }
}

/**
 * Triggers Gemini 3.5 Pro executive decision briefing and podcast script regeneration.
 * @param {string} projectSlug 
 * @param {Object} options 
 * @returns {Promise<Object>}
 */
export async function regenerateBriefing(projectSlug = 'sample', options = {}) {
    const slug = projectSlug || store.get('projectSlug') || 'sample';
    try {
        const res = await fetch(`/api/regenerate-briefing?project=${slug}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(options)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.error('[API] Failed to regenerate briefing:', err);
        throw err;
    }
}
