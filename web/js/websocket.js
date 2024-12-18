class WebSocketManager {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            reconnectAttempts: 5,
            reconnectDelay: 5000,
            heartbeatInterval: 30000,
            ...options
        };
        this.handlers = new Map();
        this.connect();
    }

    connect() {
        this.ws = new WebSocket(this.url);
        this.setupEventHandlers();
        this.startHeartbeat();
    }

    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type && this.handlers.has(data.type)) {
                this.handlers.get(data.type)(data.data);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.stopHeartbeat();
            this.reconnect();
        };
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, this.options.heartbeatInterval);
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
    }

    reconnect() {
        let attempts = 0;
        const tryReconnect = () => {
            if (attempts < this.options.reconnectAttempts) {
                attempts++;
                console.log(`Reconnection attempt ${attempts}/${this.options.reconnectAttempts}`);
                this.connect();
            }
        };

        setTimeout(tryReconnect, this.options.reconnectDelay);
    }

    on(type, handler) {
        this.handlers.set(type, handler);
    }

    off(type) {
        this.handlers.delete(type);
    }

    send(type, data) {
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type, data }));
        }
    }
}
