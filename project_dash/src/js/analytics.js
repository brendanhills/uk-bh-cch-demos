// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Pure Analytics & Calculation Engine
// Google Standards Compliant (go/tsstyle, go/js-practices)
// Zero DOM Dependencies — 100% Pure, Testable Mathematical Functions
// =============================================================================

export const MATRIX_SCORES_TABLE = [
    [15, 19, 22, 24, 25],
    [10, 14, 17, 20, 23],
    [6, 9, 13, 16, 18],
    [3, 5, 8, 11, 12],
    [1, 2, 4, 7, 21]
];

export const CONSEQUENCE_NAMES = [
    'Catastrophic',
    'Major',
    'Moderate',
    'Minor',
    'Insignificant'
];

export const LIKELIHOOD_NAMES = [
    '1 Rare',
    '2 Improbable',
    '3 Occasional',
    '4 Probable',
    '5 Almost Certain'
];

/**
 * Calculates or looks up the canonical 5x5 Risk Matrix score for given Likelihood (1-5) and Consequence (1-5).
 * @param {number} likelihood (1 to 5)
 * @param {number} consequence (1 to 5)
 * @returns {number} Matrix Score (1 to 25)
 */
export function calculateMatrixScore(likelihood, consequence) {
    const l = Math.max(1, Math.min(5, parseInt(likelihood, 10) || 1));
    const c = Math.max(1, Math.min(5, parseInt(consequence, 10) || 1));
    const cIdx = 5 - c; // 5 -> 0, 4 -> 1, 3 -> 2, 2 -> 3, 1 -> 4
    const lIdx = l - 1; // 1 -> 0, 2 -> 1, 3 -> 2, 4 -> 3, 5 -> 4
    return MATRIX_SCORES_TABLE[cIdx][lIdx];
}

/**
 * Returns the CSS styling classes corresponding to a matrix score band.
 * @param {number} score 
 * @returns {string} Tailwind CSS class string
 */
export function getScoreBadgeClass(score) {
    if (score >= 23) return 'bg-red-600 text-white border-red-700';
    if (score >= 18) return 'bg-orange-500 text-white border-orange-600';
    if (score >= 13) return 'bg-amber-100 text-amber-950 border-amber-300';
    if (score >= 7) return 'bg-emerald-600 text-white border-emerald-700';
    return 'bg-emerald-100 text-emerald-900 border-emerald-300';
}

/**
 * Filters a list of risk objects by lifecycle status.
 * @param {Array<Object>} risks 
 * @param {string} status ('open', 'active', 'eventuated', 'closed', 'all')
 * @returns {Array<Object>}
 */
export function filterRisksByStatus(risks = [], status = 'open') {
    const s = (status || 'open').toLowerCase();
    return risks.filter(r => {
        const rStatus = (r.status || 'Active').toLowerCase();
        if (s === 'open') return rStatus !== 'closed';
        if (s === 'active') return rStatus === 'active';
        if (s === 'eventuated') return rStatus === 'issue eventuated' || rStatus === 'eventuated';
        if (s === 'closed') return rStatus === 'closed';
        return true;
    });
}

/**
 * Filters risks belonging to a specific 5x5 heatmap coordinate.
 * @param {Array<Object>} risks 
 * @param {number} likelihood (1 to 5)
 * @param {number} consequence (1 to 5)
 * @param {string} ratingType ('inherent' or 'residual')
 * @returns {Array<Object>}
 */
export function filterRisksByCell(risks = [], likelihood, consequence, ratingType = 'inherent') {
    const lVal = parseInt(likelihood, 10);
    const cVal = parseInt(consequence, 10);
    const isResidual = ratingType === 'residual';

    return risks.filter(r => {
        const l = isResidual ? (r.residualLikelihood ?? r.inherentLikelihood) : r.inherentLikelihood;
        const c = isResidual ? (r.residualConsequence ?? r.inherentConsequence) : r.inherentConsequence;
        return l === lVal && c === cVal;
    });
}

/**
 * Computes high-level KPI aggregations from a risk dataset.
 * @param {Array<Object>} risks 
 * @returns {Object} { total, open, active, eventuated, closed, criticalCount, highCount, mediumCount, lowCount }
 */
export function computeRiskKpis(risks = []) {
    let open = 0, active = 0, eventuated = 0, closed = 0;
    let criticalCount = 0, highCount = 0, mediumCount = 0, lowCount = 0;

    for (const r of risks) {
        const status = (r.status || 'Active').toLowerCase();
        if (status === 'closed') closed++;
        else {
            open++;
            if (status === 'active') active++;
            if (status === 'issue eventuated' || status === 'eventuated') eventuated++;
        }

        const score = r.inherentScore || calculateMatrixScore(r.inherentLikelihood, r.inherentConsequence);
        if (score >= 20) criticalCount++;
        else if (score >= 15) highCount++;
        else if (score >= 8) mediumCount++;
        else lowCount++;
    }

    return {
        total: risks.length,
        open,
        active,
        eventuated,
        closed,
        criticalCount,
        highCount,
        mediumCount,
        lowCount
    };
}

/**
 * Computes longitudinal velocity trends and delta metrics across historical snapshot weeks.
 * @param {Object} snapshots Object keyed by week ('w22', 'w23', ...)
 * @returns {Array<Object>} Sorted chronological trend records
 */
export function computeVelocityTrends(snapshots = {}) {
    const weeks = Object.keys(snapshots).sort();
    const timeline = [];

    for (let i = 0; i < weeks.length; i++) {
        const wKey = weeks[i];
        const snap = snapshots[wKey];
        if (!snap) continue;

        const label = snap.week || snap.weekLabel || ('Week ' + (snap.weekNumber || (i + 1)));
        const total = snap.totalRisks || (snap.risks ? snap.risks.length : 0);
        const open = snap.openRisks || total;
        const critical = snap.criticalRisks || 0;

        let openedDelta = 0;
        let closedDelta = 0;

        if (i > 0) {
            const prev = timeline[i - 1];
            const netChange = open - prev.open;
            if (netChange > 0) openedDelta = netChange;
            else if (netChange < 0) closedDelta = Math.abs(netChange);
        }

        timeline.push({
            weekKey: wKey,
            label,
            date: snap.date || '',
            total,
            open,
            critical,
            openedDelta,
            closedDelta,
            netVelocity: openedDelta - closedDelta
        });
    }

    return timeline;
}

/**
 * Formats clean, safe text strings, replacing null/undefined with graceful fallbacks.
 * @param {string|null} val 
 * @param {string} fallback 
 * @returns {string}
 */
export function cleanField(val, fallback = 'N/A') {
    if (val === null || val === undefined) return fallback;
    const str = String(val).trim();
    return str.length > 0 ? str : fallback;
}
