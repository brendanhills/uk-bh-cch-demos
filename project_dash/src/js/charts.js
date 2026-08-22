// =============================================================================
// Project Monaro / F-DSE Risk Intelligence — Chart.js Lifecycle Manager
// =============================================================================

let chartBacklogInstance = null;
let chartBurndownInstance = null;

/**
 * Initializes and updates the Performance Trends charts (Risk Volume Backlog & Burndown).
 * @param {Array<Object>} timelineData 
 * @param {Function} onWeekClick Callback when a week column is clicked
 */
export function renderTrendsCharts(timelineData = [], onWeekClick = null) {
    const labels = timelineData.map(d => d.label || d.weekKey);
    const totalRisks = timelineData.map(d => d.total);
    const openRisks = timelineData.map(d => d.open);
    const criticalRisks = timelineData.map(d => d.critical);
    const netVelocity = timelineData.map(d => d.netVelocity);

    // 1. Backlog Volume Chart
    const canvasBacklog = document.getElementById('chartBacklogTimeline');
    if (canvasBacklog && typeof Chart !== 'undefined') {
        if (chartBacklogInstance) chartBacklogInstance.destroy();

        const ctx = canvasBacklog.getContext('2d');
        chartBacklogInstance = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Critical Risks',
                        data: criticalRisks,
                        backgroundColor: 'rgba(234, 67, 53, 0.85)',
                        borderColor: '#ea4335',
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: 'Active Open Risks',
                        data: openRisks,
                        backgroundColor: 'rgba(79, 70, 229, 0.85)',
                        borderColor: '#4f46e5',
                        borderWidth: 1,
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                onClick: (evt, elements) => {
                    if (elements && elements.length > 0 && typeof onWeekClick === 'function') {
                        const index = elements[0].index;
                        onWeekClick(timelineData[index], index);
                    }
                },
                plugins: {
                    legend: { position: 'top', labels: { font: { weight: 'bold', size: 11 } } },
                    tooltip: { padding: 10, cornerRadius: 8 }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } }
                }
            }
        });
    }

    // 2. Burndown Velocity Chart
    const canvasBurndown = document.getElementById('chartBurndownTimeline');
    if (canvasBurndown && typeof Chart !== 'undefined') {
        if (chartBurndownInstance) chartBurndownInstance.destroy();

        const ctx2 = canvasBurndown.getContext('2d');
        chartBurndownInstance = new Chart(ctx2, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Net Risk Velocity',
                        data: netVelocity,
                        borderColor: '#4f46e5',
                        backgroundColor: 'rgba(79, 70, 229, 0.12)',
                        borderWidth: 2.5,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                onClick: (evt, elements) => {
                    if (elements && elements.length > 0 && typeof onWeekClick === 'function') {
                        const index = elements[0].index;
                        onWeekClick(timelineData[index], index);
                    }
                },
                plugins: {
                    legend: { position: 'top', labels: { font: { weight: 'bold', size: 11 } } }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { grid: { color: 'rgba(0,0,0,0.05)' } }
                }
            }
        });
    }
}
