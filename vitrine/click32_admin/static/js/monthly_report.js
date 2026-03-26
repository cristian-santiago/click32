Chart.register(ChartDataLabels);

/* ── Paleta navy/cyan para os gráficos ── */
const CHART_COLORS = [
    '#2c3e50','#3b566e','#1a7fa8','#009fc2','#00b7eb',
    '#00ccff','#0077a3','#34495e','#1a5276','#005f7a'
];
const CHART_BORDERS = CHART_COLORS.map(c => c);

/* ── Gráfico de linha — Evolução Diária ── */
function initDailyClicksChart(labels, data) {
    const canvas = document.getElementById('dailyClicksChart');
    if (!canvas) return;

    const ctxLine = canvas.getContext('2d');
    new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cliques Diários',
                data: data,
                borderColor: '#00b7eb',
                backgroundColor: function(context) {
                    const chart = context.chart;
                    const { ctx: chartCtx, chartArea } = chart;
                    if (!chartArea) return null;
                    const gradient = chartCtx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                    gradient.addColorStop(0, 'rgba(0,204,255,0.35)');
                    gradient.addColorStop(1, 'rgba(44,62,80,0.05)');
                    return gradient;
                },
                fill: true,
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: '#00b7eb',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                tension: 0.35
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Evolução Diária de Cliques',
                    color: '#2c3e50',
                    font: { size: 12, weight: '700', family: "'Outfit', sans-serif" }
                },
                datalabels: {
                    color: '#2c3e50',
                    font: { weight: '700', size: 8, family: "'Outfit', sans-serif" },
                    formatter: function(value) { return value > 0 ? value : ''; },
                    anchor: 'end',
                    align: 'top',
                    offset: 4
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Dias', color: '#3b566e', font: { size: 9 } },
                    ticks: { color: '#2c3e50', autoSkip: false, maxTicksLimit: 30, font: { size: 7, weight: '600' } },
                    grid: { display: false }
                },
                y: {
                    title: { display: true, text: 'Cliques', color: '#3b566e', font: { size: 9 } },
                    ticks: { color: '#2c3e50', stepSize: 10, font: { size: 8, weight: '600' } },
                    grid: { color: 'rgba(0,204,255,0.08)' }
                }
            }
        }
    });
}

/* ── Gráfico de barras — Distribuição por Link ── */
function initLinkDistributionChart(labels, data) {
    const canvas = document.getElementById('linkDistributionChart');
    if (!canvas) return;

    const ctxBar = canvas.getContext('2d');
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cliques',
                data: data,
                backgroundColor: CHART_COLORS,
                borderColor: CHART_BORDERS,
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                            const percent = total > 0 ? ((context.parsed.x / total) * 100).toFixed(1) : '0';
                            return `${context.parsed.x} cliques (${percent}%)`;
                        }
                    }
                },
                datalabels: {
                    color: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        const maxValue = Math.max(...context.dataset.data);
                        return value >= maxValue * 0.2 ? '#ffffff' : '#2c3e50';
                    },
                    font: { weight: '700', size: 9, family: "'Outfit', sans-serif" },
                    formatter: function(value) { return value + ' cliques'; },
                    anchor: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        const maxValue = Math.max(...context.dataset.data);
                        return value >= maxValue * 0.2 ? 'center' : 'end';
                    },
                    align: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        const maxValue = Math.max(...context.dataset.data);
                        return value >= maxValue * 0.2 ? 'center' : 'end';
                    },
                    offset: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        const maxValue = Math.max(...context.dataset.data);
                        return value >= maxValue * 0.2 ? 0 : 8;
                    },
                    textStrokeColor: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        const maxValue = Math.max(...context.dataset.data);
                        return value >= maxValue * 0.2 ? 'rgba(0,0,0,0.45)' : 'transparent';
                    },
                    textStrokeWidth: 2,
                    display: function(context) { return context.dataset.data[context.dataIndex] > 0; },
                    clamp: true
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Quantidade de Cliques', color: '#3b566e', font: { size: 10, weight: '600' } },
                    ticks: { color: '#2c3e50', font: { size: 9 } },
                    grid: { color: 'rgba(0,204,255,0.08)' }
                },
                y: {
                    ticks: { color: '#2c3e50', font: { size: 9, weight: '700' } },
                    grid: { display: false }
                }
            },
            layout: { padding: { right: 55 } }
        },
        plugins: [ChartDataLabels]
    });
}