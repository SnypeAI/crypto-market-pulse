// Chart configurations and utilities
const chartConfigs = {
    // Technical Analysis Charts
    technical: {
        candlestick: {
            type: 'candlestick',
            options: {
                plugins: {
                    title: { display: true, text: 'Price Action' },
                    legend: { display: false }
                },
                scales: {
                    y: { position: 'right' }
                }
            }
        },
        volume: {
            type: 'bar',
            options: {
                plugins: {
                    title: { display: true, text: 'Volume Profile' }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        position: 'right'
                    }
                }
            }
        },
        indicators: {
            type: 'line',
            options: {
                plugins: {
                    title: { display: true, text: 'Technical Indicators' }
                },
                scales: {
                    y: { position: 'right' }
                }
            }
        }
    },
    
    // Model Performance Charts
    performance: {
        accuracy: {
            type: 'line',
            options: {
                plugins: {
                    title: { display: true, text: 'Model Accuracy' }
                },
                scales: {
                    y: {
                        min: 0.8,
                        max: 1.0
                    }
                }
            }
        },
        predictions: {
            type: 'scatter',
            options: {
                plugins: {
                    title: { display: true, text: 'Prediction vs Actual' }
                }
            }
        },
        alerts: {
            type: 'bar',
            options: {
                plugins: {
                    title: { display: true, text: 'Alert Distribution' }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        }
    }
};

class ChartManager {
    constructor() {
        this.charts = {};
        this.initializeCharts();
    }

    initializeCharts() {
        // Technical Analysis Charts
        this.charts.candlestick = this.createChart('candlestick-chart', chartConfigs.technical.candlestick);
        this.charts.volume = this.createChart('volume-chart', chartConfigs.technical.volume);
        this.charts.indicators = this.createChart('indicators-chart', chartConfigs.technical.indicators);

        // Model Performance Charts
        this.charts.accuracy = this.createChart('accuracy-chart', chartConfigs.performance.accuracy);
        this.charts.predictions = this.createChart('predictions-chart', chartConfigs.performance.predictions);
        this.charts.alerts = this.createChart('alerts-chart', chartConfigs.performance.alerts);
    }

    createChart(elementId, config) {
        const ctx = document.getElementById(elementId);
        return new Chart(ctx, {
            type: config.type,
            data: { datasets: [] },
            options: config.options
        });
    }

    updateCharts(data) {
        this.updateTechnicalCharts(data.technical);
        this.updatePerformanceCharts(data.performance);
    }

    updateTechnicalCharts(data) {
        // Update candlestick chart
        this.charts.candlestick.data.datasets = [{
            data: data.candlesticks
        }];
        this.charts.candlestick.update();

        // Update volume chart
        this.charts.volume.data.datasets = [{
            data: data.volume
        }];
        this.charts.volume.update();

        // Update indicators chart
        this.charts.indicators.data.datasets = [
            {
                label: 'RSI',
                data: data.rsi
            },
            {
                label: 'MACD',
                data: data.macd
            }
        ];
        this.charts.indicators.update();
    }

    updatePerformanceCharts(data) {
        // Update accuracy chart
        this.charts.accuracy.data.datasets = [{
            label: 'Model Accuracy',
            data: data.accuracy
        }];
        this.charts.accuracy.update();

        // Update predictions chart
        this.charts.predictions.data.datasets = [{
            label: 'Predictions vs Actual',
            data: data.predictions
        }];
        this.charts.predictions.update();

        // Update alerts chart
        this.charts.alerts.data.datasets = [{
            label: 'Alerts',
            data: data.alerts
        }];
        this.charts.alerts.update();
    }
}

// Export the ChartManager
window.ChartManager = ChartManager;