class CryptoApp {
    constructor() {
        this.apiUrl = '/api';
        this.symbol = 'BTC';
        this.chartManager = new ChartManager();
        this.retryAttempts = 3;
        this.retryDelay = 5000; // 5 seconds
        this.initializeApp();
    }

    initializeApp() {
        // Event listeners
        document.getElementById('symbolSelect').addEventListener('change', (e) => {
            this.symbol = e.target.value;
            this.updateAll();
        });

        // Initialize WebSocket connection
        this.initializeWebSocket();

        // Initial update
        this.updateAll();

        // Regular polling fallback
        setInterval(() => this.updateAll(), 30000);
    }

    initializeWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/api/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleRealtimeUpdate(data);
        };

        this.ws.onclose = () => {
            console.log('WebSocket connection closed. Retrying...');
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }

    async updateAll() {
        try {
            const updates = await Promise.all([
                this.fetchWithRetry(() => this.fetchMarketData()),
                this.fetchWithRetry(() => this.fetchTechnicalData()),
                this.fetchWithRetry(() => this.fetchPerformanceData())
            ]);

            this.updateUI(...updates);
        } catch (error) {
            this.handleError(error);
        }
    }

    async fetchWithRetry(fetchFn, attempts = this.retryAttempts) {
        for (let i = 0; i < attempts; i++) {
            try {
                return await fetchFn();
            } catch (error) {
                if (i === attempts - 1) throw error;
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            }
        }
    }

    async fetchMarketData() {
        const response = await fetch(`${this.apiUrl}/market/${this.symbol}`);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    }

    handleRealtimeUpdate(data) {
        switch (data.type) {
            case 'market':
                this.updateMarketData(data.data);
                break;
            case 'technical':
                this.chartManager.updateTechnicalCharts(data.data);
                break;
            case 'performance':
                this.chartManager.updatePerformanceCharts(data.data);
                break;
            case 'alert':
                this.handleAlert(data.data);
                break;
        }
    }

    handleAlert(alert) {
        // Add alert to list
        const alertsList = document.getElementById('alertsList');
        const alertElement = document.createElement('div');
        alertElement.className = 'alert-item flex items-center justify-between p-3 bg-gray-700 rounded mb-2';
        alertElement.innerHTML = `
            <div class="flex items-center">
                <span class="${this.getAlertClass(alert.severity)} mr-2">${alert.icon}</span>
                <span>${alert.message}</span>
            </div>
            <span class="text-sm text-gray-400">${this.formatTime(new Date())}</span>
        `;

        // Prepend new alert
        alertsList.insertBefore(alertElement, alertsList.firstChild);

        // Remove old alerts
        while (alertsList.children.length > 10) {
            alertsList.removeChild(alertsList.lastChild);
        }

        // Show notification if supported
        if (Notification.permission === 'granted') {
            new Notification('Crypto Market Alert', {
                body: alert.message,
                icon: '/img/icon.png'
            });
        }
    }

    handleError(error) {
        console.error('Application error:', error);
        
        // Show error in UI
        const errorBanner = document.createElement('div');
        errorBanner.className = 'bg-red-500 text-white px-4 py-2 fixed top-0 left-0 right-0 text-center';
        errorBanner.textContent = `Error: ${error.message}. Retrying...`;
        document.body.prepend(errorBanner);

        // Remove banner after 5 seconds
        setTimeout(() => errorBanner.remove(), 5000);
    }

    formatTime(date) {
        return date.toLocaleTimeString();
    }

    getAlertClass(severity) {
        const classes = {
            high: 'text-red-500',
            medium: 'text-yellow-500',
            low: 'text-blue-500'
        };
        return classes[severity] || 'text-gray-500';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CryptoApp();
});