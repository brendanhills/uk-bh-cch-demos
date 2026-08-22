// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Performance Trends Controller
// =============================================================================

import { store } from '../state.js';
import { computeVelocityTrends } from '../analytics.js';
import { renderTrendsCharts } from '../charts.js';

export function renderTrendsOverview() {
    const snaps = store.get('timeMachineSnapshots') || {};
    const timelineData = computeVelocityTrends(snaps);

    renderTrendsCharts(timelineData, (weekItem) => {
        if (weekItem && window.app && window.app.activateTimeMachine) {
            window.app.activateTimeMachine(weekItem.weekKey);
        }
    });
}
