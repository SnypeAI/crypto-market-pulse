// Fetch and update data
async function fetchData() {
    try {
        const response = await fetch('data/latest.json');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Update dashboard with new data
function updateDashboard(data) {
    updatePredictions(data.predictions);
    updateCharts(data);
    updateAlerts(data.monitoring.alerts);
}

// Initialize charts
function initCharts() {
    // Predictions chart
    const predChart = new Chart(
        document.getElementById('predictions-chart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'BTC Predictions',
                    data: [],
                    borderColor: '#60A5FA',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        }
    );

    // Performance chart
    const perfChart = new Chart(
        document.getElementById('performance-chart'),
        {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Model Accuracy',
                    data: [],
                    borderColor: '#34D399',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        min: 0.9,
                        max: 1.0
                    }
                }
            }
        }
    );

    return { predChart, perfChart };
}

// Start the application
const charts = initCharts();
fetchData();
setInterval(fetchData, 60000); // Update every minute